"""Testes de rejeição determinística no engine (ADR-0004).

Cobrem os 5 gatilhos: zero, negativo, NaN, inf, acima do cap.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from alpha_forge.backtest.cost import zero_cost
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.backtest.schemas import RejectionReason, Signal
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.base import Strategy


class AlwaysLong(Strategy):
    name = "always_long"

    def decide(self, window: pd.DataFrame) -> Signal:
        return Signal.ENTER_LONG if len(window) == 1 else Signal.HOLD


def _make_prices(opens: list[float]) -> pd.DataFrame:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    idx = pd.date_range(start=start, periods=len(opens), freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open": opens,
            "high": [p * 1.01 for p in opens],
            "low": [p * 0.99 for p in opens],
            "close": opens,
            "volume": [100.0] * len(opens),
        },
        index=idx,
    )


def test_rejeita_preco_zero_como_size_inf() -> None:
    prices = _make_prices([100.0, 0.0, 100.0])
    budget = RiskBudget(capital_inicial=1000.0, fracao_por_trade=0.1, alavancagem_max=1.0)
    result = run_backtest(
        prices=prices,
        strategy=AlwaysLong(),
        budget=budget,
        cost_model=zero_cost(),
        dataset_id="test",
    )
    assert len(result.fills) == 0
    assert len(result.rejections) == 1
    assert result.rejections[0].reason == RejectionReason.SIZE_INF


def test_rejeita_acima_do_cap_quando_fracao_alta() -> None:
    prices = _make_prices([100.0, 100.0, 100.0])
    budget = RiskBudget(capital_inicial=1000.0, fracao_por_trade=1.0, alavancagem_max=10.0)

    class Poison(Strategy):
        name = "poison"

        def decide(self, window: pd.DataFrame) -> Signal:
            return Signal.ENTER_LONG if len(window) == 1 else Signal.HOLD

    result = _run_with_patched_sizing(
        prices, Poison(), budget, lambda *_args, **_kw: 10_000.0
    )
    assert any(
        r.reason == RejectionReason.ABOVE_LEVERAGE_CAP for r in result.rejections
    )
    assert len(result.fills) == 0


def test_rejeita_size_zero() -> None:
    prices = _make_prices([100.0, 100.0, 100.0])
    budget = RiskBudget(capital_inicial=1000.0, fracao_por_trade=0.1, alavancagem_max=1.0)
    result = _run_with_patched_sizing(prices, AlwaysLong(), budget, lambda *_a, **_k: 0.0)
    assert any(r.reason == RejectionReason.SIZE_ZERO for r in result.rejections)
    assert len(result.fills) == 0


def test_rejeita_size_negativo() -> None:
    prices = _make_prices([100.0, 100.0, 100.0])
    budget = RiskBudget(capital_inicial=1000.0, fracao_por_trade=0.1, alavancagem_max=1.0)
    result = _run_with_patched_sizing(prices, AlwaysLong(), budget, lambda *_a, **_k: -1.0)
    assert any(r.reason == RejectionReason.SIZE_NEGATIVE for r in result.rejections)


def test_rejeita_size_nan() -> None:
    prices = _make_prices([100.0, 100.0, 100.0])
    budget = RiskBudget(capital_inicial=1000.0, fracao_por_trade=0.1, alavancagem_max=1.0)
    result = _run_with_patched_sizing(prices, AlwaysLong(), budget, lambda *_a, **_k: float("nan"))
    assert any(r.reason == RejectionReason.SIZE_NAN for r in result.rejections)


def _run_with_patched_sizing(prices, strategy, budget, sizing_fn):
    """Substitui temporariamente o sizing usado pelo engine."""
    import alpha_forge.backtest.engine as engine_mod

    original = engine_mod.fixed_fractional_position_sizing
    engine_mod.fixed_fractional_position_sizing = sizing_fn  # type: ignore[assignment]
    try:
        return run_backtest(
            prices=prices,
            strategy=strategy,
            budget=budget,
            cost_model=zero_cost(),
            dataset_id="test",
        )
    finally:
        engine_mod.fixed_fractional_position_sizing = original  # type: ignore[assignment]


@pytest.fixture(autouse=True)
def _ensure_engine_restored():
    import alpha_forge.backtest.engine as engine_mod
    from alpha_forge.risk.sizing import fixed_fractional_position_sizing as real

    yield
    engine_mod.fixed_fractional_position_sizing = real  # type: ignore[assignment]
