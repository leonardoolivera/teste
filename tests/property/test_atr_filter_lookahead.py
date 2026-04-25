"""Property-based: ``ATRRegimeFilter`` não pode consumir ``window.iloc[-1]``.

Invariante causal (ADR-0002 + ADR-0022 §contrato): o filtro decide sobre
a barra ``t`` lendo apenas ``window.iloc[:-1]``. Perturbar a última linha
de ``window`` com valores extremos **não pode** alterar ``is_active``.

Estratégia idêntica a ``test_regime_filter_lookahead.py`` mas sobre ATR:
precisa de colunas ``high``, ``low``, ``close`` para True Range.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from alpha_forge.regimes import ATRRegimeFilter


def _window_from_returns(returns: list[float]) -> pd.DataFrame:
    arr = np.array(returns, dtype=float)
    close = 100.0 * np.exp(np.cumsum(arr))
    # synthetic high/low around close to ensure TR is well-defined
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
    atr_window=st.integers(min_value=5, max_value=20),
    min_atr_bps=st.floats(min_value=0.0, max_value=200.0, allow_nan=False),
)
@settings(max_examples=40, deadline=None)
def test_atr_regime_ignora_barra_t(
    returns: list[float], atr_window: int, min_atr_bps: float
) -> None:
    window = _window_from_returns(returns)
    filt = ATRRegimeFilter(window=atr_window, min_atr_bps=min_atr_bps)

    baseline = filt.is_active(window)

    perturbed = window.copy()
    last = len(perturbed) - 1
    perturbed.iloc[last, perturbed.columns.get_loc("close")] = 1e9
    perturbed.iloc[last, perturbed.columns.get_loc("high")] = 1e9
    perturbed.iloc[last, perturbed.columns.get_loc("low")] = 1e9
    assert baseline == filt.is_active(perturbed)

    annihilated = window.copy()
    annihilated.iloc[last, annihilated.columns.get_loc("close")] = 1e-9
    annihilated.iloc[last, annihilated.columns.get_loc("high")] = 1e-9
    annihilated.iloc[last, annihilated.columns.get_loc("low")] = 1e-9
    assert baseline == filt.is_active(annihilated)
