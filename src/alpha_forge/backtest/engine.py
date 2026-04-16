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
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol, cast

import pandas as pd

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
from alpha_forge.risk.schemas import RiskBudget
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


def run_backtest(
    *,
    prices: pd.DataFrame,
    strategy: StrategyProtocol,
    budget: RiskBudget,
    cost_model: CostModel,
    dataset_id: str,
) -> BacktestResult:
    """Executa o backtest causal e devolve `BacktestResult`.

    `prices` deve conter colunas ``open, high, low, close`` indexadas por
    ``DatetimeIndex``. `cost_model` é obrigatório (ADR-0006); para rodar sem
    custo, passe ``zero_cost()`` explicitamente.
    """
    _validate_prices(prices)

    n = len(prices)
    position = _Position()
    fills: list[Fill] = []
    rejections: list[Rejection] = []
    trades: list[Trade] = []
    equity_curve: list[tuple[pd.Timestamp, float]] = []
    raw_signals: list[int] = []

    closes = cast(pd.Series, prices["close"])
    opens = cast(pd.Series, prices["open"])
    timestamps = cast(pd.DatetimeIndex, prices.index)

    for t in range(n):
        window = prices.iloc[: t + 1]
        signal = strategy.decide(window)
        raw_signals.append(_signal_to_int(signal))

        ts_signal = cast(pd.Timestamp, timestamps[t])

        if t + 1 < n:
            ts_exec = cast(pd.Timestamp, timestamps[t + 1])
            market_price = float(cast(float, opens.iloc[t + 1]))
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

        mark_price = float(cast(float, closes.iloc[t]))
        equity = _mark_to_market(budget.capital_inicial, position, mark_price, trades)
        equity_curve.append((ts_signal, equity))

    assert_causal(
        pd.Series(raw_signals, index=prices.index, name="signal"),
        closes,
    )

    equity_values = [e for _, e in equity_curve]
    final_equity = equity_values[-1] if equity_values else budget.capital_inicial

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

    if position.side != Side.FLAT:
        return

    side = Side.LONG if signal == Signal.ENTER_LONG else Side.SHORT
    notional_estimate = budget.capital_inicial * budget.fracao_por_trade * budget.alavancagem_max
    exec_price = apply_cost(
        price_market=market_price,
        notional=notional_estimate,
        capital_inicial=budget.capital_inicial,
        side=side,
        is_entry=True,
        cost_model=cost_model,
    )

    raw_size = fixed_fractional_position_sizing(
        budget=budget, preco_entrada=exec_price, capital_corrente=budget.capital_inicial
    )
    reason = _classify_size(raw_size, exec_price, budget.capital_inicial, budget)
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
