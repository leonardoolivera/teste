"""Property-based: ``BollingerWidthFilter`` não pode consumir ``window.iloc[-1]``.

Invariante causal (ADR-0002 + ADR-0022 §contrato): o filtro decide sobre
a barra ``t`` lendo apenas ``window.iloc[:-1]``. Perturbar a última linha
de ``window`` com valores extremos **não pode** alterar ``is_active``.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from alpha_forge.regimes import BollingerWidthFilter


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
        min_size=40,
        max_size=150,
    ),
    window=st.integers(min_value=5, max_value=30),
    num_std=st.floats(min_value=0.5, max_value=3.0, allow_nan=False),
    min_width_bps=st.floats(min_value=0.0, max_value=500.0, allow_nan=False),
)
@settings(max_examples=40, deadline=None)
def test_bollinger_width_ignora_barra_t(
    returns: list[float],
    window: int,
    num_std: float,
    min_width_bps: float,
) -> None:
    df = _window_from_returns(returns)
    filt = BollingerWidthFilter(
        window=window, num_std=num_std, min_width_bps=min_width_bps
    )
    baseline = filt.is_active(df)

    perturbed = df.copy()
    last = len(perturbed) - 1
    perturbed.iloc[last, perturbed.columns.get_loc("close")] = 1e9
    perturbed.iloc[last, perturbed.columns.get_loc("high")] = 1e9
    perturbed.iloc[last, perturbed.columns.get_loc("low")] = 1e9
    assert baseline == filt.is_active(perturbed)

    annihilated = df.copy()
    annihilated.iloc[last, annihilated.columns.get_loc("close")] = 1e-9
    annihilated.iloc[last, annihilated.columns.get_loc("high")] = 1e-9
    annihilated.iloc[last, annihilated.columns.get_loc("low")] = 1e-9
    assert baseline == filt.is_active(annihilated)
