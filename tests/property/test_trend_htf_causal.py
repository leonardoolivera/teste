"""Property-based: TrendHTFRegimeFilter respeita causalidade (ADR-0002 + ADR-0043).

Mutar window.iloc[-1] não pode alterar is_active. Alem disso, o filter
descarta o último candle HTF do resample, então mutações na última barra
LTF (que pode cair no bucket HTF aberto) não afetam decisão.
"""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from alpha_forge.regimes import TrendHTFRegimeFilter


def _window_from_returns(returns: list[float]) -> pd.DataFrame:
    arr = np.array(returns, dtype=float)
    close = 100.0 * np.exp(np.cumsum(arr))
    high = close * 1.002
    low = close * 0.998
    idx = pd.date_range(
        start=datetime(2024, 1, 1, tzinfo=timezone.utc),
        periods=len(close),
        freq="1h",
        tz="UTC",
    )
    return pd.DataFrame(
        {"open": close, "high": high, "low": low, "close": close, "volume": 1.0},
        index=idx,
    )


@given(
    returns=st.lists(
        st.floats(min_value=-0.02, max_value=0.02, allow_nan=False, allow_infinity=False),
        min_size=300,
        max_size=600,
    ),
    sma_window=st.integers(min_value=5, max_value=30),
    mode=st.sampled_from(["long_only", "short_only", "both_sides"]),
)
@settings(max_examples=20, deadline=None)
def test_trend_htf_ignora_barra_t(
    returns: list[float], sma_window: int, mode: str
) -> None:
    window = _window_from_returns(returns)
    filt = TrendHTFRegimeFilter(htf="4h", sma_window=sma_window, mode=mode)
    baseline = filt.is_active(window)

    perturbed = window.copy()
    last = len(perturbed) - 1
    for col in ("open", "high", "low", "close"):
        perturbed.iloc[last, perturbed.columns.get_loc(col)] = 1e9
    assert filt.is_active(perturbed) == baseline

    annihilated = window.copy()
    for col in ("open", "high", "low", "close"):
        annihilated.iloc[last, annihilated.columns.get_loc(col)] = 1e-9
    assert filt.is_active(annihilated) == baseline
