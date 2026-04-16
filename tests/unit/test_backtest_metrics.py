"""Testes unitários das métricas mínimas (ADR-0007)."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from alpha_forge.backtest.cost import zero_cost
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.backtest.metrics import compute_metrics
from alpha_forge.backtest.schemas import (
    BacktestResult,
    Side,
    Signal,
    Trade,
)
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.base import Strategy


def _empty_result(equity: list[tuple[datetime, float]], trades: list[Trade]) -> BacktestResult:
    return BacktestResult(
        dataset_id="test",
        bars=len(equity),
        fills=[],
        rejections=[],
        trades=trades,
        final_equity=equity[-1][1] if equity else 1000.0,
        max_equity=max(v for _, v in equity) if equity else 1000.0,
        min_equity=min(v for _, v in equity) if equity else 1000.0,
        equity_curve=equity,
    )


def test_metrics_zero_trades_hit_rate_none() -> None:
    ts0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    equity = [(ts0, 1000.0), (ts0, 1000.0), (ts0, 1000.0)]
    m = compute_metrics(_empty_result(equity, []), capital_inicial=1000.0)
    assert m.trade_count == 0
    assert m.hit_rate is None
    assert m.max_drawdown == 0.0
    assert m.total_pnl == pytest.approx(0.0)


def test_metrics_equity_flat() -> None:
    ts0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    equity = [(ts0, 1000.0)] * 10
    m = compute_metrics(_empty_result(equity, []), capital_inicial=1000.0)
    assert m.max_drawdown == 0.0
    assert m.total_pnl == pytest.approx(0.0)


def test_metrics_max_drawdown_calculado_corretamente() -> None:
    ts0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    equity = [
        (ts0, 1000.0),
        (ts0, 1200.0),
        (ts0, 900.0),
        (ts0, 1100.0),
        (ts0, 800.0),
    ]
    m = compute_metrics(_empty_result(equity, []), capital_inicial=1000.0)
    assert m.max_drawdown == pytest.approx(1.0 - 800.0 / 1200.0)


def test_metrics_hit_rate_com_trades_conhecidos() -> None:
    ts0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    trades = [
        Trade(
            side=Side.LONG,
            entry_timestamp=ts0,
            exit_timestamp=ts0,
            entry_price=100.0,
            exit_price=110.0,
            size=1.0,
            pnl=10.0,
        ),
        Trade(
            side=Side.LONG,
            entry_timestamp=ts0,
            exit_timestamp=ts0,
            entry_price=100.0,
            exit_price=95.0,
            size=1.0,
            pnl=-5.0,
        ),
        Trade(
            side=Side.SHORT,
            entry_timestamp=ts0,
            exit_timestamp=ts0,
            entry_price=100.0,
            exit_price=90.0,
            size=1.0,
            pnl=10.0,
        ),
    ]
    equity = [(ts0, 1000.0), (ts0, 1015.0)]
    m = compute_metrics(_empty_result(equity, trades), capital_inicial=1000.0)
    assert m.trade_count == 3
    assert m.hit_rate == pytest.approx(2 / 3)
    assert m.total_pnl == pytest.approx(15.0)


class OnlyEnterOnce(Strategy):
    name = "only_enter_once"

    def decide(self, window: pd.DataFrame) -> Signal:
        return Signal.ENTER_LONG if len(window) == 1 else Signal.HOLD


def test_metrics_posicao_aberta_no_fim_nao_conta_como_trade() -> None:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    idx = pd.date_range(start=start, periods=5, freq="1h", tz="UTC")
    prices = pd.DataFrame(
        {
            "open": [100.0, 100.0, 105.0, 105.0, 110.0],
            "high": [101.0, 101.0, 106.0, 106.0, 111.0],
            "low": [99.0, 99.0, 104.0, 104.0, 109.0],
            "close": [100.0, 105.0, 105.0, 110.0, 110.0],
            "volume": [10.0] * 5,
        },
        index=idx,
    )
    budget = RiskBudget(capital_inicial=1000.0, fracao_por_trade=0.1, alavancagem_max=1.0)
    result = run_backtest(
        prices=prices,
        strategy=OnlyEnterOnce(),
        budget=budget,
        cost_model=zero_cost(),
        dataset_id="test",
    )
    assert len(result.trades) == 0
    assert result.final_equity > budget.capital_inicial
    assert result.metrics is not None
    assert result.metrics.trade_count == 0
    assert result.metrics.hit_rate is None
    assert result.metrics.total_pnl > 0.0
