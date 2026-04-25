"""Property-based: ``CompositeFilter`` preserva causalidade (ADR-0023).

A composição de filtros causais é causal: perturbar ``window.iloc[-1]``
não pode alterar ``is_active`` de ``CompositeFilter([...])``. Herdada
diretamente da propriedade de cada filtro interno + ``all``/``any``
sobre resultados determinísticos.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from alpha_forge.regimes import ATRRegimeFilter, CompositeFilter, SMASlopeFilter


def _window_from_returns(returns: list[float]) -> pd.DataFrame:
    arr = np.array(returns, dtype=float)
    close = 100.0 * np.exp(np.cumsum(arr))
    high = close * 1.005
    low = close * 0.995
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
        st.floats(min_value=-0.05, max_value=0.05, allow_nan=False, allow_infinity=False),
        min_size=70,
        max_size=200,
    ),
    mode=st.sampled_from(["and", "or"]),
    min_slope_bps=st.floats(min_value=0.0, max_value=30.0, allow_nan=False),
    min_atr_bps=st.floats(min_value=0.0, max_value=200.0, allow_nan=False),
)
@settings(max_examples=30, deadline=None)
def test_composite_ignora_barra_t(
    returns: list[float],
    mode: str,
    min_slope_bps: float,
    min_atr_bps: float,
) -> None:
    window = _window_from_returns(returns)
    sma = SMASlopeFilter(window=50, min_slope_bps=min_slope_bps)
    atr = ATRRegimeFilter(window=14, min_atr_bps=min_atr_bps)
    comp = CompositeFilter([sma, atr], mode=mode)  # type: ignore[arg-type]

    baseline = comp.is_active(window)

    for sentinel in (1e9, 1e-9):
        perturbed = window.copy()
        last = len(perturbed) - 1
        for col in ("close", "high", "low", "open"):
            perturbed.iloc[last, perturbed.columns.get_loc(col)] = sentinel
        assert baseline == comp.is_active(perturbed)
