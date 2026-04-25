"""Testes ADR-0063 — sizing dual (fixed_notional + snowball)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from alpha_forge.backtest.cost import CostModel, zero_cost
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.backtest.schemas import Signal
from alpha_forge.risk.schemas import RiskBudget, SizingMode


class _OneShotStrategy:
    """Estrategia minima: emite um par (ENTER_LONG, EXIT) nos indices dados."""

    def __init__(self, enter_at: int, exit_at: int) -> None:
        self.enter_at = enter_at
        self.exit_at = exit_at
        self._idx = -1

    def decide(self, window: pd.DataFrame) -> Signal:
        self._idx += 1
        if self._idx == self.enter_at:
            return Signal.ENTER_LONG
        if self._idx == self.exit_at:
            return Signal.EXIT
        return Signal.HOLD


class _MultiTradeStrategy:
    """Estrategia com N trades pre-definidos (enter, exit alternados)."""

    def __init__(self, signals: list[Signal]) -> None:
        self._signals = signals
        self._idx = -1

    def decide(self, window: pd.DataFrame) -> Signal:
        self._idx += 1
        if self._idx < len(self._signals):
            return self._signals[self._idx]
        return Signal.HOLD


def _prices_linear(n: int, start: float, step: float) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    closes = np.array([start + step * i for i in range(n)], dtype=float)
    opens = np.concatenate([[closes[0]], closes[:-1]])
    return pd.DataFrame(
        {"open": opens, "high": closes, "low": opens, "close": closes},
        index=idx,
    )


class TestSizingModeDefault:
    def test_budget_default_e_fixed_notional(self) -> None:
        budget = RiskBudget(capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0)
        assert budget.sizing_mode == SizingMode.FIXED_NOTIONAL


class TestFixedVsSnowballEquivalente:
    def test_um_trade_fixed_e_snowball_dao_mesmo_size(self) -> None:
        prices = _prices_linear(10, 100.0, 1.0)
        strat = _OneShotStrategy(enter_at=1, exit_at=5)

        budget_fixed = RiskBudget(
            capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0,
            sizing_mode=SizingMode.FIXED_NOTIONAL,
        )
        res_fixed = run_backtest(
            prices=prices, strategy=strat, budget=budget_fixed,
            cost_model=zero_cost(), dataset_id="t1",
        )

        strat2 = _OneShotStrategy(enter_at=1, exit_at=5)
        budget_snow = RiskBudget(
            capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0,
            sizing_mode=SizingMode.SNOWBALL,
        )
        res_snow = run_backtest(
            prices=prices, strategy=strat2, budget=budget_snow,
            cost_model=zero_cost(), dataset_id="t1",
        )

        # No primeiro trade nao ha realized PnL acumulado; sizes batem.
        assert res_fixed.trades[0].size == pytest.approx(res_snow.trades[0].size)
        assert res_fixed.trades[0].pnl == pytest.approx(res_snow.trades[0].pnl)


class TestSnowballCapitalizaAposWin:
    def test_segundo_trade_snowball_maior_que_fixed_apos_win(self) -> None:
        # Prices sobem linearmente: long vence; snowball capitaliza.
        prices = _prices_linear(30, 100.0, 1.0)
        signals = [Signal.HOLD] * 2 + [Signal.ENTER_LONG] + [Signal.HOLD] * 5 + [Signal.EXIT] + \
                  [Signal.HOLD] * 3 + [Signal.ENTER_LONG] + [Signal.HOLD] * 5 + [Signal.EXIT] + [Signal.HOLD] * 12

        strat = _MultiTradeStrategy(signals.copy())
        budget_fixed = RiskBudget(
            capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0,
            sizing_mode=SizingMode.FIXED_NOTIONAL,
        )
        res_fixed = run_backtest(
            prices=prices, strategy=strat, budget=budget_fixed,
            cost_model=zero_cost(), dataset_id="t2",
        )

        strat2 = _MultiTradeStrategy(signals.copy())
        budget_snow = RiskBudget(
            capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0,
            sizing_mode=SizingMode.SNOWBALL,
        )
        res_snow = run_backtest(
            prices=prices, strategy=strat2, budget=budget_snow,
            cost_model=zero_cost(), dataset_id="t2",
        )

        assert len(res_fixed.trades) == 2
        assert len(res_snow.trades) == 2
        # Trade 1 deve ser identico.
        assert res_fixed.trades[0].size == pytest.approx(res_snow.trades[0].size)
        # Trade 2: snowball > fixed em size (capital_corrente ja incluiu win do trade 1).
        assert res_snow.trades[1].size > res_fixed.trades[1].size
        # Consequentemente snowball final_equity > fixed final_equity.
        assert res_snow.final_equity > res_fixed.final_equity


class TestSnowballDeduzAposLoss:
    def test_segundo_trade_snowball_menor_apos_loss(self) -> None:
        # Prices caem: long perde; snowball deduz capital corrente.
        prices = _prices_linear(30, 100.0, -0.5)  # decrescente
        signals = [Signal.HOLD] * 2 + [Signal.ENTER_LONG] + [Signal.HOLD] * 5 + [Signal.EXIT] + \
                  [Signal.HOLD] * 3 + [Signal.ENTER_LONG] + [Signal.HOLD] * 5 + [Signal.EXIT] + [Signal.HOLD] * 12

        strat_fixed = _MultiTradeStrategy(signals.copy())
        budget_fixed = RiskBudget(
            capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0,
            sizing_mode=SizingMode.FIXED_NOTIONAL,
        )
        res_fixed = run_backtest(
            prices=prices, strategy=strat_fixed, budget=budget_fixed,
            cost_model=zero_cost(), dataset_id="t3",
        )

        strat_snow = _MultiTradeStrategy(signals.copy())
        budget_snow = RiskBudget(
            capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0,
            sizing_mode=SizingMode.SNOWBALL,
        )
        res_snow = run_backtest(
            prices=prices, strategy=strat_snow, budget=budget_snow,
            cost_model=zero_cost(), dataset_id="t3",
        )

        assert len(res_fixed.trades) == 2
        assert len(res_snow.trades) == 2
        assert res_fixed.trades[0].pnl < 0  # loss confirmado
        # Trade 2 snowball: size menor que fixed porque capital_corrente caiu.
        assert res_snow.trades[1].size < res_fixed.trades[1].size
        # Loss total snowball MENOR em magnitude que fixed (deducao protege).
        # PnL negativos: snowball > fixed (menos negativo).
        assert res_snow.final_equity > res_fixed.final_equity


class TestSnowballPreservaRuntimeContract:
    def test_snowball_ainda_emite_trades_com_mesmo_shape(self) -> None:
        prices = _prices_linear(20, 100.0, 1.0)
        strat = _OneShotStrategy(enter_at=1, exit_at=5)
        budget = RiskBudget(
            capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0,
            sizing_mode=SizingMode.SNOWBALL,
        )
        res = run_backtest(
            prices=prices, strategy=strat, budget=budget,
            cost_model=zero_cost(), dataset_id="t4",
        )
        assert len(res.trades) == 1
        assert len(res.fills) == 2  # entry + exit
        assert res.trades[0].pnl is not None
