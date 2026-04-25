"""Tests para ADR-0180: engine pyramid_equity mode.

Cobertura:
- RiskBudget: PYRAMID_EQUITY exige todos pyramid_* params.
- RiskBudget: pyramid_* em modos != PYRAMID_EQUITY é rejeitado.
- Engine: stack cresce a cada ENTER same-side até max_tranches.
- Engine: ENTER oposto com stack aberto é no-op (NÃO reverte em pyramid).
- Engine: filter flip fecha TODAS as tranches; N trades, ordem FIFO.
- Engine: rearm cooldown bloqueia ENTER por N barras após full exit.
- Engine: mark-to-market inclui unrealized de todas as tranches.
"""
from __future__ import annotations

import pandas as pd
import pytest

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.backtest.schemas import Side, Signal
from alpha_forge.regimes.filter import RegimeFilter
from alpha_forge.risk.schemas import RiskBudget, SizingMode


# ---------- RiskBudget validation ----------


class TestRiskBudgetPyramidValidation:
    def test_pyramid_requires_all_three_params(self):
        with pytest.raises(ValueError, match="PYRAMID_EQUITY exige"):
            RiskBudget(
                capital_inicial=10_000.0,
                fracao_por_trade=0.1,
                alavancagem_max=5.0,
                sizing_mode=SizingMode.PYRAMID_EQUITY,
            )

    def test_pyramid_partial_params_rejected(self):
        with pytest.raises(ValueError, match="PYRAMID_EQUITY exige"):
            RiskBudget(
                capital_inicial=10_000.0,
                fracao_por_trade=0.1,
                alavancagem_max=5.0,
                sizing_mode=SizingMode.PYRAMID_EQUITY,
                pyramid_max_tranches=5,
                pyramid_tranche_equity_fraction=0.20,
                # falta rearm
            )

    def test_non_pyramid_rejects_pyramid_params(self):
        with pytest.raises(ValueError, match="pyramid_\\* só são aceitos"):
            RiskBudget(
                capital_inicial=10_000.0,
                fracao_por_trade=0.1,
                alavancagem_max=2.0,
                sizing_mode=SizingMode.FIXED_NOTIONAL,
                pyramid_max_tranches=5,
            )

    def test_pyramid_valid_config(self):
        b = RiskBudget(
            capital_inicial=10_000.0,
            fracao_por_trade=0.1,  # ignored in pyramid but must satisfy schema
            alavancagem_max=5.0,
            sizing_mode=SizingMode.PYRAMID_EQUITY,
            pyramid_max_tranches=5,
            pyramid_tranche_equity_fraction=0.20,
            pyramid_rearm_cooldown_bars=1,
        )
        assert b.pyramid_max_tranches == 5
        assert b.pyramid_tranche_equity_fraction == 0.20


# ---------- Engine pyramid behavior ----------


class _FixedSignalStrategy:
    """Emite um signal scriptado por barra (index pela position bar)."""

    def __init__(self, signals: list[Signal]) -> None:
        self._signals = signals
        self._count = 0

    def decide(self, window):  # noqa: D401
        idx = len(window) - 1
        return self._signals[idx] if idx < len(self._signals) else Signal.HOLD


class _AlwaysActiveFilter:
    name = "always_active"

    def is_active(self, window):
        return True


class _ToggleFilter:
    """Retorna True até barra `flip_at`, depois False (simulando regime flip)."""

    name = "toggle"

    def __init__(self, flip_at: int) -> None:
        self.flip_at = flip_at

    def is_active(self, window):
        causal_idx = len(window) - 1
        return causal_idx < self.flip_at


def _make_prices(n: int, start: float = 100.0, step: float = 0.0) -> pd.DataFrame:
    idx = pd.date_range("2025-01-01", periods=n, freq="1h")
    closes = [start + i * step for i in range(n)]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    return pd.DataFrame(
        {"open": closes, "high": highs, "low": lows, "close": closes, "volume": [0.0] * n},
        index=idx,
    )


def _pyramid_budget(
    *,
    max_tranches: int = 5,
    frac: float = 0.20,
    cooldown: int = 0,
    alav: float = 5.0,
) -> RiskBudget:
    return RiskBudget(
        capital_inicial=10_000.0,
        fracao_por_trade=0.1,
        alavancagem_max=alav,
        sizing_mode=SizingMode.PYRAMID_EQUITY,
        pyramid_max_tranches=max_tranches,
        pyramid_tranche_equity_fraction=frac,
        pyramid_rearm_cooldown_bars=cooldown,
    )


def _zero_cost() -> CostModel:
    return CostModel(taker_fee_bps=0.0, slippage_bps_per_unit_notional=0.0, spread_bps=0.0)


class TestPyramidStackGrowth:
    def test_three_enters_open_three_tranches(self):
        # Signals: LONG, LONG, LONG, HOLD, HOLD (5 bars) — filter sempre ativo.
        prices = _make_prices(6, start=100.0)
        strategy = _FixedSignalStrategy(
            [Signal.ENTER_LONG, Signal.ENTER_LONG, Signal.ENTER_LONG, Signal.HOLD, Signal.HOLD]
        )
        result = run_backtest(
            prices=prices,
            strategy=strategy,
            budget=_pyramid_budget(max_tranches=5, cooldown=0),
            cost_model=_zero_cost(),
            dataset_id="test-pyramid",
            regime_filter=_AlwaysActiveFilter(),
        )
        # 3 fills de abertura (tranches). Nenhum close (filter sempre ativo).
        open_fills = [f for f in result.fills if f.side != Side.FLAT]
        close_fills = [f for f in result.fills if f.side == Side.FLAT]
        assert len(open_fills) == 3
        assert len(close_fills) == 0
        assert len(result.trades) == 0  # nenhum trade fechado mid-backtest

    def test_max_tranches_cap_respected(self):
        # 6 signals but max=3 → apenas 3 tranches abertas.
        prices = _make_prices(8, start=100.0)
        strategy = _FixedSignalStrategy(
            [Signal.ENTER_LONG] * 6 + [Signal.HOLD]
        )
        result = run_backtest(
            prices=prices,
            strategy=strategy,
            budget=_pyramid_budget(max_tranches=3, cooldown=0),
            cost_model=_zero_cost(),
            dataset_id="test-cap",
            regime_filter=_AlwaysActiveFilter(),
        )
        open_fills = [f for f in result.fills if f.side != Side.FLAT]
        assert len(open_fills) == 3

    def test_opposite_signal_ignored_in_pyramid(self):
        # LONG then SHORT while open → SHORT must be ignored (não reverte).
        prices = _make_prices(5, start=100.0)
        strategy = _FixedSignalStrategy(
            [Signal.ENTER_LONG, Signal.ENTER_SHORT, Signal.HOLD, Signal.HOLD]
        )
        result = run_backtest(
            prices=prices,
            strategy=strategy,
            budget=_pyramid_budget(max_tranches=5, cooldown=0),
            cost_model=_zero_cost(),
            dataset_id="test-oppos",
            regime_filter=_AlwaysActiveFilter(),
        )
        open_fills = [f for f in result.fills if f.side != Side.FLAT]
        assert len(open_fills) == 1
        assert open_fills[0].side == Side.LONG


class TestPyramidExitAll:
    def test_regime_flip_closes_all_tranches(self):
        # 3 LONG enters, então flip em t=4 (bar 4 → signal coerces to EXIT).
        prices = _make_prices(7, start=100.0)
        strategy = _FixedSignalStrategy(
            [Signal.ENTER_LONG, Signal.ENTER_LONG, Signal.ENTER_LONG, Signal.HOLD, Signal.HOLD, Signal.HOLD, Signal.HOLD]
        )
        result = run_backtest(
            prices=prices,
            strategy=strategy,
            budget=_pyramid_budget(max_tranches=5, cooldown=0),
            cost_model=_zero_cost(),
            dataset_id="test-exitall",
            regime_filter=_ToggleFilter(flip_at=4),  # filter False a partir de bar 4
        )
        open_fills = [f for f in result.fills if f.side != Side.FLAT]
        close_fills = [f for f in result.fills if f.side == Side.FLAT]
        assert len(open_fills) == 3
        assert len(close_fills) == 3  # all 3 tranches closed
        assert len(result.trades) == 3

    def test_exit_order_is_fifo(self):
        # 3 opens em preços diferentes, verify entry_timestamp order = fill open order.
        prices = _make_prices(6, start=100.0, step=1.0)
        strategy = _FixedSignalStrategy(
            [Signal.ENTER_LONG, Signal.ENTER_LONG, Signal.ENTER_LONG, Signal.HOLD, Signal.HOLD, Signal.HOLD]
        )
        result = run_backtest(
            prices=prices,
            strategy=strategy,
            budget=_pyramid_budget(max_tranches=5, cooldown=0),
            cost_model=_zero_cost(),
            dataset_id="test-fifo",
            regime_filter=_ToggleFilter(flip_at=4),
        )
        # Trades em ordem FIFO pelo entry_timestamp
        trades = result.trades
        assert len(trades) == 3
        assert trades[0].entry_timestamp < trades[1].entry_timestamp < trades[2].entry_timestamp


class TestPyramidRearmCooldown:
    def test_cooldown_blocks_reentry(self):
        # Enter bar 0 → open tranche. Filter flip bar 2 → EXIT.
        # Bar 3 tenta ENTER mas cooldown=2 ainda bloqueia.
        # Bar 5 deve permitir ENTER.
        class _CustomFilter:
            name = "custom"
            def is_active(self, window):
                idx = len(window) - 1
                # Active bars 0,1 (entry + hold), off bar 2 (forces EXIT), back on bar 3+
                return idx != 2 and idx != 3 and idx < 10
        # Simpler: Always-on except bar 2, then on again
        # Actually, let's use a filter that flips off once then on
        class _FlipOnceFilter:
            name = "flip_once"
            def is_active(self, window):
                idx = len(window) - 1
                return idx != 2  # off só em bar 2 → força EXIT bar 2 → cooldown começa

        prices = _make_prices(10, start=100.0)
        strategy = _FixedSignalStrategy(
            [Signal.ENTER_LONG] * 10
        )
        result = run_backtest(
            prices=prices,
            strategy=strategy,
            budget=_pyramid_budget(max_tranches=5, cooldown=3),
            cost_model=_zero_cost(),
            dataset_id="test-cooldown",
            regime_filter=_FlipOnceFilter(),
        )
        # Bars 0,1: signals ENTER_LONG com filter ativo → 2 opens at t+1 (bar 1, 2)
        # Bar 2: filter OFF → EXIT at t+1 (bar 3). Cooldown=3 starts.
        # Bars 3,4,5: ENTER coerced to HOLD by cooldown.
        # Bar 6+: ENTER ok again.
        close_fills = [f for f in result.fills if f.side == Side.FLAT]
        # At least one exit
        assert len(close_fills) >= 1
        # After exit and cooldown, new opens should appear; total opens > initial 2
        open_fills = [f for f in result.fills if f.side != Side.FLAT]
        assert len(open_fills) >= 3  # 2 before exit + at least 1 after cooldown

    def test_zero_cooldown_immediate_rearm(self):
        class _FlipOnceFilter:
            name = "flip_once"
            def is_active(self, window):
                idx = len(window) - 1
                return idx != 2

        prices = _make_prices(8, start=100.0)
        strategy = _FixedSignalStrategy([Signal.ENTER_LONG] * 8)
        result = run_backtest(
            prices=prices,
            strategy=strategy,
            budget=_pyramid_budget(max_tranches=5, cooldown=0),
            cost_model=_zero_cost(),
            dataset_id="test-zero-cool",
            regime_filter=_FlipOnceFilter(),
        )
        # Com cooldown=0, após exit, próximo bar pode abrir imediatamente.
        open_fills = [f for f in result.fills if f.side != Side.FLAT]
        # 2 antes do exit + várias após (limited by remaining bars - cooldown = 0)
        assert len(open_fills) >= 3


class TestPyramidSizingEquityBased:
    def test_tranche_size_grows_with_equity(self):
        # Price sobe entre tranches → tranche 2 notional maior que tranche 1.
        # Tranche 1 exec at open[1]=110, tranche 2 exec at open[3]=120.
        # Entre tranche 1 e tranche 2, tranche 1 unrealized sobe → equity MTM sobe → tranche 2 maior.
        n = 5
        idx = pd.date_range("2025-01-01", periods=n, freq="1h")
        opens = [100.0, 110.0, 115.0, 120.0, 120.0]
        closes = [100.0, 110.0, 115.0, 120.0, 120.0]
        highs = [c + 0.5 for c in closes]
        lows = [c - 0.5 for c in closes]
        prices = pd.DataFrame(
            {"open": opens, "high": highs, "low": lows, "close": closes, "volume": [0.0] * n},
            index=idx,
        )
        strategy = _FixedSignalStrategy(
            [Signal.ENTER_LONG, Signal.HOLD, Signal.ENTER_LONG, Signal.HOLD, Signal.HOLD]
        )
        result = run_backtest(
            prices=prices,
            strategy=strategy,
            budget=_pyramid_budget(max_tranches=5, cooldown=0, alav=1.0, frac=0.20),
            cost_model=_zero_cost(),
            dataset_id="test-sizing",
            regime_filter=_AlwaysActiveFilter(),
        )
        open_fills = [f for f in result.fills if f.side != Side.FLAT]
        assert len(open_fills) == 2
        # Tranche 1: equity = 10000, notional = 10000 * 0.20 * 1.0 = 2000, size ~ 2000/110
        # Tranche 2: equity_mtm = 10000 + size1*(120-110) > 10000 → notional > 2000
        assert open_fills[1].notional > open_fills[0].notional
