"""Property-based tests do guardião de causalidade (ADR-0002).

Estratégia:
- Geramos séries de preço adversariais com hypothesis.
- Sinal causal (baseado em `close.shift(1)`) deve passar.
- Sinal que espia o futuro (`close.shift(-1)`) deve ser pego.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from alpha_forge.backtest.lookahead_guard import LookaheadViolation, assert_causal


def _index(n: int) -> pd.DatetimeIndex:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return pd.date_range(start=start, periods=n, freq="1h", tz="UTC")


@given(
    returns=st.lists(
        st.floats(min_value=-0.05, max_value=0.05, allow_nan=False, allow_infinity=False),
        min_size=60,
        max_size=200,
    ),
    seed=st.integers(min_value=0, max_value=10_000),
)
@settings(max_examples=30, deadline=None)
def test_guard_aceita_sinal_causal(returns: list[float], seed: int) -> None:
    prices = _prices_from_returns(returns)
    rng = np.random.default_rng(seed)
    noise = rng.choice([-1, 0, 1], size=len(prices), p=[0.2, 0.6, 0.2])
    signals_series = pd.Series(noise, index=prices.index, dtype=float)
    assert_causal(signals_series, prices)


@given(
    returns=st.lists(
        st.floats(min_value=-0.05, max_value=0.05, allow_nan=False, allow_infinity=False),
        min_size=60,
        max_size=200,
    ),
)
@settings(max_examples=20, deadline=None)
def test_guard_detecta_peek_do_futuro(returns: list[float]) -> None:
    prices = _prices_from_returns(returns)
    future_returns = prices.pct_change().shift(-1).fillna(0.0)
    cheating = np.sign(future_returns).astype(float)
    if (cheating != 0).sum() < 10:
        pytest.skip("não há sinais ativos suficientes para caracterizar peek")
    with pytest.raises(LookaheadViolation):
        assert_causal(cheating, prices)


def _prices_from_returns(returns: list[float]) -> pd.Series:
    arr = np.array(returns, dtype=float)
    close = 100.0 * np.exp(np.cumsum(arr))
    return pd.Series(close, index=_index(len(close)), name="close")
