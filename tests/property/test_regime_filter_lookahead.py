"""Property-based: ``RegimeFilter`` não pode consumir ``window.iloc[-1]``.

Invariante causal (ADR-0002 + ADR-0022 §contrato): o filtro decide sobre
a barra ``t`` lendo apenas ``window.iloc[:-1]``. Perturbar a última linha
de ``window`` com valores extremos **não pode** alterar ``is_active``.

Estratégia:
- Gera ``window`` sintético de ``n`` barras.
- Computa ``is_active(window)`` do ``SMASlopeFilter``.
- Substitui ``window.iloc[-1]`` por ``close=1e9`` (valor adversarial).
- Re-computa ``is_active`` e exige igualdade bit-a-bit.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from alpha_forge.regimes import SMASlopeFilter


def _window_from_returns(returns: list[float]) -> pd.DataFrame:
    arr = np.array(returns, dtype=float)
    close = 100.0 * np.exp(np.cumsum(arr))
    idx = pd.date_range(
        start=datetime(2024, 1, 1, tzinfo=timezone.utc),
        periods=len(close),
        freq="1h",
        tz="UTC",
    )
    return pd.DataFrame({"close": close}, index=idx)


@given(
    returns=st.lists(
        st.floats(min_value=-0.05, max_value=0.05, allow_nan=False, allow_infinity=False),
        min_size=60,
        max_size=200,
    ),
    sma_window=st.integers(min_value=5, max_value=30),
    min_slope_bps=st.floats(min_value=0.0, max_value=50.0, allow_nan=False),
)
@settings(max_examples=40, deadline=None)
def test_sma_slope_ignora_barra_t(
    returns: list[float], sma_window: int, min_slope_bps: float
) -> None:
    window = _window_from_returns(returns)
    filt = SMASlopeFilter(window=sma_window, min_slope_bps=min_slope_bps)

    baseline = filt.is_active(window)

    perturbed = window.copy()
    perturbed.iloc[-1, perturbed.columns.get_loc("close")] = 1e9
    perturbed_result = filt.is_active(perturbed)

    assert baseline == perturbed_result

    annihilated = window.copy()
    annihilated.iloc[-1, annihilated.columns.get_loc("close")] = 1e-9
    annihilated_result = filt.is_active(annihilated)

    assert baseline == annihilated_result
