"""Smoke tests for SuperTrend (ADR-0193)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.families.supertrend import SuperTrendStrategy


def _make_df(closes: np.ndarray) -> pd.DataFrame:
    highs = closes + 1.0
    lows = closes - 1.0
    opens = closes.copy()
    vols = np.ones_like(closes)
    return pd.DataFrame(
        {"open": opens, "high": highs, "low": lows, "close": closes, "volume": vols}
    )


def test_warmup_returns_hold() -> None:
    s = SuperTrendStrategy(atr_period=10, atr_mult=3.0, long_only=False)
    df = _make_df(np.linspace(100, 110, 10))
    assert s.decide(df) == Signal.HOLD


def test_flip_down_produces_short() -> None:
    up = np.linspace(100, 150, 30)
    down = np.linspace(150, 100, 30)
    df = _make_df(np.concatenate([up, down]))
    s = SuperTrendStrategy(atr_period=10, atr_mult=3.0, long_only=False)
    signals = [s.decide(df.iloc[:i]).name for i in range(15, len(df) + 1)]
    assert "ENTER_SHORT" in signals


def test_long_only_exits_on_downflip() -> None:
    up = np.linspace(100, 150, 30)
    down = np.linspace(150, 100, 30)
    df = _make_df(np.concatenate([up, down]))
    s = SuperTrendStrategy(atr_period=10, atr_mult=3.0, long_only=True)
    signals = [s.decide(df.iloc[:i]).name for i in range(15, len(df) + 1)]
    assert "EXIT" in signals
    assert "ENTER_SHORT" not in signals


def test_invalid_atr_period_rejected() -> None:
    with pytest.raises(ValueError):
        SuperTrendStrategy(atr_period=0, atr_mult=3.0)
    with pytest.raises(TypeError):
        SuperTrendStrategy(atr_period=1.0, atr_mult=3.0)  # type: ignore[arg-type]


def test_invalid_atr_mult_rejected() -> None:
    with pytest.raises(ValueError):
        SuperTrendStrategy(atr_period=10, atr_mult=0.0)
    with pytest.raises(TypeError):
        SuperTrendStrategy(atr_period=10, atr_mult="3.0")  # type: ignore[arg-type]
