"""Engine de backtest causal do núcleo mínimo (ADR-0002, ADR-0004, ADR-0006, ADR-0007).

Contrato temporal (ADR-0002):
  - Estratégia vê apenas ``prices[:t+1]`` ao decidir em `t`.
  - Execução acontece em `t+1` pelo `open` da barra seguinte.
  - `assert_causal` é chamado antes de devolver resultado.

Rejeição determinística (ADR-0004):
  - Tamanho 0, negativo, NaN, inf ou acima do `alavancagem_max` → sem trade,
    evento de rejeição registrado.

Custos (ADR-0006):
  - `cost_model` é argumento obrigatório. Preço efetivo ajustado contra o
    trader em entrada e saída.

Contabilidade de trades (ADR-0007):
  - Fechamento de posição registra um `Trade` com PnL pós-custo.
  - Posição aberta ao fim do backtest **não** gera `Trade`, mas seu PnL
    mark-to-market entra no `final_equity` (e portanto em `total_pnl`).

Pyramid mode (ADR-0180):
  - Quando ``budget.sizing_mode == SizingMode.PYRAMID_EQUITY``, engine usa path
    alternativo com stack de tranches. Invariantes v4 runtime:
      - Sinal ENTER mesma direção + stack < max_tranches → nova tranche.
      - Sinal ENTER direção oposta com posição aberta → no-op (NÃO reverte,
        derroga ADR-0012 em pyramid mode).
      - Filtro inativo com posição aberta → EXIT de TODAS as tranches em open[t+1].
        FIFO para reporting; um Trade por tranche.
      - Após exit total, cooldown de rearm_cooldown_bars barras bloqueia ENTER.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, cast

import pandas as pd

if TYPE_CHECKING:
    from alpha_forge.regimes.filter import RegimeFilter

logger = logging.getLogger("alpha_forge.backtest")

from alpha_forge.backtest.cost import CostModel, apply_cost
from alpha_forge.backtest.lookahead_guard import assert_causal
from alpha_forge.backtest.metrics import compute_metrics
from alpha_forge.backtest.schemas import (
    BacktestResult,
    Fill,
    Rejection,
    RejectionReason,
    Side,
    Signal,
    Trade,
)
from alpha_forge.risk.schemas import RiskBudget, SizingMode
from alpha_forge.risk.sizing import fixed_fractional_position_sizing


class StrategyProtocol(Protocol):
    """Contrato estrutural da estratégia (ADR-0002, Contrato A: janela causal).

    A cada barra `t`, o engine entrega ``window = prices[:t+1]`` e a estratégia
    retorna um `Signal`. A estratégia **não tem acesso ao dataset completo**.
    """

    def decide(self, window: pd.DataFrame) -> Signal: ...


@dataclass
class _Position:
    side: Side = Side.FLAT
    size: float = 0.0
    entry_price: float = 0.0
    entry_timestamp: pd.Timestamp | None = None


@dataclass
class _Tranche:
    """Tranche individual de uma posição pyramid (ADR-0180)."""

    side: Side
    size: float
    entry_price: float
    entry_timestamp: pd.Timestamp


@dataclass
class _PyramidPosition:
    """Stack FIFO de tranches para pyramid mode (ADR-0180)."""

    tranches: list[_Tranche]

    @property
    def side(self) -> Side:
        if not self.tranches:
            return Side.FLAT
        return self.tranches[0].side

    @property
    def is_flat(self) -> bool:
        return len(self.tranches) == 0


def run_backtest(
    *,
    prices: pd.DataFrame,
    strategy: StrategyProtocol,
    budget: RiskBudget,
    cost_model: CostModel,
    dataset_id: str,
    regime_filter: "RegimeFilter | None" = None,
) -> BacktestResult:
    """Executa o backtest causal e devolve `BacktestResult`.

    `prices` deve conter colunas ``open, high, low, close`` indexadas por
    ``DatetimeIndex``. `cost_model` é obrigatório (ADR-0006); para rodar sem
    custo, passe ``zero_cost()`` explicitamente.

    ``regime_filter`` (ADR-0022) é opcional: quando fornecido, o sinal da
    estratégia é coercivamente substituído por ``HOLD`` (se flat) ou
    ``EXIT`` (se posicionado) sempre que ``filter.is_active(window)`` for
    ``False``. Default ``None`` preserva comportamento bit-a-bit.
    """
    _validate_prices(prices)

    n = len(prices)
    logger.info(
        "backtest.start dataset_id=%s bars=%d strategy=%s capital=%.2f fee_bps=%.4f slip_bps=%.4f sizing=%s",
        dataset_id,
        n,
        type(strategy).__name__,
        budget.capital_inicial,
        cost_model.taker_fee_bps,
        cost_model.slippage_bps_per_unit_notional,
        budget.sizing_mode.value,
    )
    is_pyramid = budget.sizing_mode == SizingMode.PYRAMID_EQUITY
    position = _Position()
    pyramid_position = _PyramidPosition(tranches=[])
    fills: list[Fill] = []
    rejections: list[Rejection] = []
    trades: list[Trade] = []
    equity_curve: list[tuple[pd.Timestamp, float]] = []
    raw_signals: list[int] = []
    # Pyramid rearm state: bars_since_full_exit counts up while flat; negative = never exited.
    pyramid_cooldown_remaining = 0

    closes = cast(pd.Series, prices["close"])
    opens = cast(pd.Series, prices["open"])
    timestamps = cast(pd.DatetimeIndex, prices.index)

    for t in range(n):
        window = prices.iloc[: t + 1]
        signal = strategy.decide(window)

        # ADR-0022: regime filter coerce (opt-in).
        if regime_filter is not None and not regime_filter.is_active(window):
            current_side = pyramid_position.side if is_pyramid else position.side
            if current_side == Side.FLAT:
                signal = Signal.HOLD
            else:
                signal = Signal.EXIT

        # ADR-0180: rearm cooldown coerces ENTER to HOLD while counting down.
        if is_pyramid and pyramid_cooldown_remaining > 0 and signal in (
            Signal.ENTER_LONG,
            Signal.ENTER_SHORT,
        ):
            signal = Signal.HOLD

        raw_signals.append(_signal_to_int(signal))

        ts_signal = cast(pd.Timestamp, timestamps[t])

        if t + 1 < n:
            ts_exec = cast(pd.Timestamp, timestamps[t + 1])
            market_price = float(cast(float, opens.iloc[t + 1]))
            if is_pyramid:
                was_flat_before = pyramid_position.is_flat
                _apply_signal_at_next_open_pyramid(
                    signal=signal,
                    ts_signal=ts_signal,
                    ts_exec=ts_exec,
                    market_price=market_price,
                    budget=budget,
                    cost_model=cost_model,
                    position=pyramid_position,
                    fills=fills,
                    rejections=rejections,
                    trades=trades,
                )
                # Cooldown starts the bar AFTER full exit (decremented at end of each bar).
                if not was_flat_before and pyramid_position.is_flat:
                    assert budget.pyramid_rearm_cooldown_bars is not None
                    pyramid_cooldown_remaining = budget.pyramid_rearm_cooldown_bars
            else:
                _apply_signal_at_next_open(
                    signal=signal,
                    ts_signal=ts_signal,
                    ts_exec=ts_exec,
                    market_price=market_price,
                    budget=budget,
                    cost_model=cost_model,
                    position=position,
                    fills=fills,
                    rejections=rejections,
                    trades=trades,
                )

        if is_pyramid and pyramid_cooldown_remaining > 0:
            pyramid_cooldown_remaining -= 1

        mark_price = float(cast(float, closes.iloc[t]))
        if is_pyramid:
            equity = _mark_to_market_pyramid(
                budget.capital_inicial, pyramid_position, mark_price, trades
            )
        else:
            equity = _mark_to_market(budget.capital_inicial, position, mark_price, trades)
        equity_curve.append((ts_signal, equity))

    assert_causal(
        pd.Series(raw_signals, index=prices.index, name="signal"),
        closes,
    )

    equity_values = [e for _, e in equity_curve]
    final_equity = equity_values[-1] if equity_values else budget.capital_inicial

    logger.info(
        "backtest.end dataset_id=%s bars=%d fills=%d rejections=%d trades=%d final_equity=%.2f",
        dataset_id,
        n,
        len(fills),
        len(rejections),
        len(trades),
        final_equity,
    )

    result = BacktestResult(
        dataset_id=dataset_id,
        bars=n,
        fills=fills,
        rejections=rejections,
        trades=trades,
        final_equity=final_equity,
        max_equity=max(equity_values) if equity_values else budget.capital_inicial,
        min_equity=min(equity_values) if equity_values else budget.capital_inicial,
        equity_curve=[(ts.to_pydatetime(), v) for ts, v in equity_curve],
    )
    metrics = compute_metrics(result, capital_inicial=budget.capital_inicial)
    return result.model_copy(update={"metrics": metrics})


def _apply_signal_at_next_open(
    *,
    signal: Signal,
    ts_signal: pd.Timestamp,
    ts_exec: pd.Timestamp,
    market_price: float,
    budget: RiskBudget,
    cost_model: CostModel,
    position: _Position,
    fills: list[Fill],
    rejections: list[Rejection],
    trades: list[Trade],
) -> None:
    if signal == Signal.HOLD:
        return

    if signal == Signal.EXIT:
        _close_position(
            ts_signal=ts_signal,
            ts_exec=ts_exec,
            market_price=market_price,
            budget=budget,
            cost_model=cost_model,
            position=position,
            fills=fills,
            trades=trades,
        )
        return

    side = Side.LONG if signal == Signal.ENTER_LONG else Side.SHORT

    if position.side != Side.FLAT:
        if position.side == side:
            # Mesma direção já aberta: sinal redundante, no-op (ADR-0008 §7, ADR-0011).
            return
        # Reverse-on-signal (ADR-0012): fecha posição atual e reabre no lado oposto,
        # ambas em `t+1 open`. Custo aplicado duas vezes (fiel à realidade). Um Trade
        # fechado registrado; dois Fills (fechamento + abertura) na mesma ts_exec.
        logger.debug(
            "engine.reverse_on_signal ts_exec=%s from=%s to=%s",
            ts_exec.isoformat(),
            position.side.name,
            side.name,
        )
        _close_position(
            ts_signal=ts_signal,
            ts_exec=ts_exec,
            market_price=market_price,
            budget=budget,
            cost_model=cost_model,
            position=position,
            fills=fills,
            trades=trades,
        )

    if budget.sizing_mode == SizingMode.SNOWBALL:
        capital_corrente = budget.capital_inicial + sum(tr.pnl for tr in trades)
    else:
        capital_corrente = budget.capital_inicial
    if capital_corrente <= 0.0:
        rejections.append(
            Rejection(
                timestamp=ts_exec.to_pydatetime(),
                signal_timestamp=ts_signal.to_pydatetime(),
                reason=RejectionReason.SIZE_ZERO,
                raw_size=0.0,
                price=market_price,
            )
        )
        return

    notional_estimate = capital_corrente * budget.fracao_por_trade * budget.alavancagem_max
    exec_price = apply_cost(
        price_market=market_price,
        notional=notional_estimate,
        capital_inicial=budget.capital_inicial,
        side=side,
        is_entry=True,
        cost_model=cost_model,
    )

    raw_size = fixed_fractional_position_sizing(
        budget=budget, preco_entrada=exec_price, capital_corrente=capital_corrente
    )
    reason = _classify_size(raw_size, exec_price, capital_corrente, budget)
    if reason is not None:
        rejections.append(
            Rejection(
                timestamp=ts_exec.to_pydatetime(),
                signal_timestamp=ts_signal.to_pydatetime(),
                reason=reason,
                raw_size=raw_size if math.isfinite(raw_size) else 0.0,
                price=exec_price,
            )
        )
        logger.debug(
            "engine.rejection ts_exec=%s reason=%s raw_size=%s price=%.6f",
            ts_exec.isoformat(),
            reason.value,
            raw_size,
            exec_price,
        )
        return

    position.side = side
    position.size = raw_size
    position.entry_price = exec_price
    position.entry_timestamp = ts_exec
    fills.append(
        Fill(
            timestamp=ts_exec.to_pydatetime(),
            signal_timestamp=ts_signal.to_pydatetime(),
            side=side,
            price=exec_price,
            size=raw_size,
            notional=raw_size * exec_price,
        )
    )
    logger.debug(
        "engine.fill.open ts_exec=%s side=%s size=%.6f price=%.6f",
        ts_exec.isoformat(),
        side.name,
        raw_size,
        exec_price,
    )


def _close_position(
    *,
    ts_signal: pd.Timestamp,
    ts_exec: pd.Timestamp,
    market_price: float,
    budget: RiskBudget,
    cost_model: CostModel,
    position: _Position,
    fills: list[Fill],
    trades: list[Trade],
) -> None:
    if position.side == Side.FLAT:
        return

    notional_estimate = position.size * market_price
    exit_price = apply_cost(
        price_market=market_price,
        notional=notional_estimate,
        capital_inicial=budget.capital_inicial,
        side=position.side,
        is_entry=False,
        cost_model=cost_model,
    )

    direction = 1.0 if position.side == Side.LONG else -1.0
    pnl = direction * position.size * (exit_price - position.entry_price)

    fills.append(
        Fill(
            timestamp=ts_exec.to_pydatetime(),
            signal_timestamp=ts_signal.to_pydatetime(),
            side=Side.FLAT,
            price=exit_price,
            size=position.size,
            notional=position.size * exit_price,
        )
    )

    assert position.entry_timestamp is not None
    trades.append(
        Trade(
            side=position.side,
            entry_timestamp=position.entry_timestamp.to_pydatetime(),
            exit_timestamp=ts_exec.to_pydatetime(),
            entry_price=position.entry_price,
            exit_price=exit_price,
            size=position.size,
            pnl=pnl,
        )
    )
    logger.debug(
        "engine.fill.close ts_exec=%s side=%s size=%.6f entry=%.6f exit=%.6f pnl=%.6f",
        ts_exec.isoformat(),
        position.side.name,
        position.size,
        position.entry_price,
        exit_price,
        pnl,
    )

    position.side = Side.FLAT
    position.size = 0.0
    position.entry_price = 0.0
    position.entry_timestamp = None


def _classify_size(
    raw_size: float, price: float, capital: float, budget: RiskBudget
) -> RejectionReason | None:
    if math.isnan(raw_size):
        return RejectionReason.SIZE_NAN
    if math.isinf(raw_size):
        return RejectionReason.SIZE_INF
    if raw_size == 0.0:
        return RejectionReason.SIZE_ZERO
    if raw_size < 0.0:
        return RejectionReason.SIZE_NEGATIVE
    exposure = (raw_size * price) / capital if capital > 0 else float("inf")
    if exposure > budget.alavancagem_max + 1e-9:
        return RejectionReason.ABOVE_LEVERAGE_CAP
    return None


def _mark_to_market(
    capital_inicial: float,
    position: _Position,
    mark_price: float,
    trades: list[Trade],
) -> float:
    realized = sum(tr.pnl for tr in trades)
    if position.side == Side.FLAT:
        return capital_inicial + realized
    direction = 1.0 if position.side == Side.LONG else -1.0
    unrealized = direction * position.size * (mark_price - position.entry_price)
    return capital_inicial + realized + unrealized


def _signal_to_int(signal: Signal) -> int:
    if signal == Signal.ENTER_LONG:
        return 1
    if signal == Signal.ENTER_SHORT:
        return -1
    return 0


def _validate_prices(prices: pd.DataFrame) -> None:
    required = {"open", "high", "low", "close"}
    missing = required - set(prices.columns)
    if missing:
        raise ValueError(f"prices sem colunas obrigatórias: {sorted(missing)}")
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise ValueError("prices.index deve ser DatetimeIndex")
    if len(prices) < 2:
        raise ValueError("prices precisa ter ao menos 2 barras")


def _apply_signal_at_next_open_pyramid(
    *,
    signal: Signal,
    ts_signal: pd.Timestamp,
    ts_exec: pd.Timestamp,
    market_price: float,
    budget: RiskBudget,
    cost_model: CostModel,
    position: _PyramidPosition,
    fills: list[Fill],
    rejections: list[Rejection],
    trades: list[Trade],
) -> None:
    """Pyramid execution path (ADR-0180).

    - ENTER same direction + stack < max → open new tranche.
    - ENTER opposite direction + stack non-empty → no-op (pyramid NÃO reverte).
    - EXIT + stack non-empty → close all tranches FIFO at the same ts_exec.
    - HOLD → no-op.
    """
    if signal == Signal.HOLD:
        return

    if signal == Signal.EXIT:
        _close_all_tranches(
            ts_signal=ts_signal,
            ts_exec=ts_exec,
            market_price=market_price,
            budget=budget,
            cost_model=cost_model,
            position=position,
            fills=fills,
            trades=trades,
        )
        return

    side = Side.LONG if signal == Signal.ENTER_LONG else Side.SHORT

    if not position.is_flat and position.side != side:
        # Reverse-on-signal NÃO se aplica em pyramid (ADR-0180 invariante #6).
        logger.debug(
            "engine.pyramid.opposite_signal_ignored ts_exec=%s stack_side=%s signal_side=%s",
            ts_exec.isoformat(),
            position.side.name,
            side.name,
        )
        return

    assert budget.pyramid_max_tranches is not None
    assert budget.pyramid_tranche_equity_fraction is not None
    if len(position.tranches) >= budget.pyramid_max_tranches:
        # Stack cheio; novo sinal ignorado até regime flip ou mudança.
        return

    # Equity mark-to-market inclui unrealized das tranches abertas (ADR-0180 invariante #3).
    equity_mtm = _mark_to_market_pyramid(
        budget.capital_inicial, position, market_price, trades
    )
    if equity_mtm <= 0.0:
        rejections.append(
            Rejection(
                timestamp=ts_exec.to_pydatetime(),
                signal_timestamp=ts_signal.to_pydatetime(),
                reason=RejectionReason.SIZE_ZERO,
                raw_size=0.0,
                price=market_price,
            )
        )
        return

    tranche_capital = equity_mtm * budget.pyramid_tranche_equity_fraction
    notional_estimate = tranche_capital * budget.alavancagem_max
    exec_price = apply_cost(
        price_market=market_price,
        notional=notional_estimate,
        capital_inicial=budget.capital_inicial,
        side=side,
        is_entry=True,
        cost_model=cost_model,
    )
    if exec_price <= 0.0:
        rejections.append(
            Rejection(
                timestamp=ts_exec.to_pydatetime(),
                signal_timestamp=ts_signal.to_pydatetime(),
                reason=RejectionReason.SIZE_ZERO,
                raw_size=0.0,
                price=market_price,
            )
        )
        return

    raw_size = notional_estimate / exec_price
    reason = _classify_size(raw_size, exec_price, equity_mtm, budget)
    if reason is not None:
        rejections.append(
            Rejection(
                timestamp=ts_exec.to_pydatetime(),
                signal_timestamp=ts_signal.to_pydatetime(),
                reason=reason,
                raw_size=raw_size if math.isfinite(raw_size) else 0.0,
                price=exec_price,
            )
        )
        return

    tranche = _Tranche(
        side=side,
        size=raw_size,
        entry_price=exec_price,
        entry_timestamp=ts_exec,
    )
    position.tranches.append(tranche)
    fills.append(
        Fill(
            timestamp=ts_exec.to_pydatetime(),
            signal_timestamp=ts_signal.to_pydatetime(),
            side=side,
            price=exec_price,
            size=raw_size,
            notional=raw_size * exec_price,
        )
    )
    logger.debug(
        "engine.pyramid.tranche_open ts_exec=%s side=%s tranche_idx=%d size=%.6f price=%.6f equity_mtm=%.2f",
        ts_exec.isoformat(),
        side.name,
        len(position.tranches),
        raw_size,
        exec_price,
        equity_mtm,
    )


def _close_all_tranches(
    *,
    ts_signal: pd.Timestamp,
    ts_exec: pd.Timestamp,
    market_price: float,
    budget: RiskBudget,
    cost_model: CostModel,
    position: _PyramidPosition,
    fills: list[Fill],
    trades: list[Trade],
) -> None:
    """Fecha todas as tranches FIFO no mesmo ts_exec (ADR-0180 invariante #7)."""
    if position.is_flat:
        return

    # FIFO: iterate in insertion order.
    for tranche in list(position.tranches):
        notional_estimate = tranche.size * market_price
        exit_price = apply_cost(
            price_market=market_price,
            notional=notional_estimate,
            capital_inicial=budget.capital_inicial,
            side=tranche.side,
            is_entry=False,
            cost_model=cost_model,
        )
        direction = 1.0 if tranche.side == Side.LONG else -1.0
        pnl = direction * tranche.size * (exit_price - tranche.entry_price)

        fills.append(
            Fill(
                timestamp=ts_exec.to_pydatetime(),
                signal_timestamp=ts_signal.to_pydatetime(),
                side=Side.FLAT,
                price=exit_price,
                size=tranche.size,
                notional=tranche.size * exit_price,
            )
        )
        trades.append(
            Trade(
                side=tranche.side,
                entry_timestamp=tranche.entry_timestamp.to_pydatetime(),
                exit_timestamp=ts_exec.to_pydatetime(),
                entry_price=tranche.entry_price,
                exit_price=exit_price,
                size=tranche.size,
                pnl=pnl,
            )
        )
        logger.debug(
            "engine.pyramid.tranche_close ts_exec=%s side=%s size=%.6f entry=%.6f exit=%.6f pnl=%.6f",
            ts_exec.isoformat(),
            tranche.side.name,
            tranche.size,
            tranche.entry_price,
            exit_price,
            pnl,
        )

    position.tranches.clear()


def _mark_to_market_pyramid(
    capital_inicial: float,
    position: _PyramidPosition,
    mark_price: float,
    trades: list[Trade],
) -> float:
    """Equity mark-to-market em pyramid mode (ADR-0180 invariante #3)."""
    realized = sum(tr.pnl for tr in trades)
    if position.is_flat:
        return capital_inicial + realized
    unrealized = 0.0
    for tranche in position.tranches:
        direction = 1.0 if tranche.side == Side.LONG else -1.0
        unrealized += direction * tranche.size * (mark_price - tranche.entry_price)
    return capital_inicial + realized + unrealized
