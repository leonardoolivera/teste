"""Property-based: ``CompositeFilter`` monotônico a **nível de signal-emission** (ADR-0023).

Reformulação post-H.5 (2026-04-18). A versão original de ADR-0023 property 1 afirmava
que AND é estritamente trade-count-restritivo, mas o piloto H.5 mostrou que a engine
de execução pode **fragmentar trades** (EXIT mid-trade + re-entrada) quando qualquer
filtro deactiva. A invariante correta é sobre **barras ativas** (quantidade de
`is_active(window_prefixo) == True` avaliado sobre cada prefixo do histórico), não
sobre transações.

- **AND-restritivo em signal-emission**: `active(and(f1,f2)) <= min(active(f1), active(f2))`.
- **OR-permissivo em signal-emission**: `active(or(f1,f2)) >= max(active(f1), active(f2))`.

Nenhuma dependência da engine — propriedade pura do combinador lógico.
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


def _count_active(filt, df: pd.DataFrame, start: int) -> int:
    """Conta barras t onde filt.is_active(df.iloc[:t+1]) == True, para t in [start, len-1]."""
    total = 0
    for t in range(start, len(df)):
        if filt.is_active(df.iloc[: t + 1]):
            total += 1
    return total


@given(
    returns=st.lists(
        st.floats(
            min_value=-0.03, max_value=0.03, allow_nan=False, allow_infinity=False
        ),
        min_size=80,
        max_size=150,
    ),
    min_slope_bps=st.floats(min_value=0.0, max_value=30.0, allow_nan=False),
    min_atr_bps=st.floats(min_value=0.0, max_value=150.0, allow_nan=False),
)
@settings(max_examples=15, deadline=None)
def test_and_restritivo_em_signal_emission(
    returns: list[float],
    min_slope_bps: float,
    min_atr_bps: float,
) -> None:
    df = _window_from_returns(returns)
    sma = SMASlopeFilter(window=50, min_slope_bps=min_slope_bps)
    atr = ATRRegimeFilter(window=14, min_atr_bps=min_atr_bps)
    comp = CompositeFilter([sma, atr], mode="and")

    start = 51  # warm-up do SMA; ambos filtros definidos a partir daqui

    n_sma = _count_active(sma, df, start)
    n_atr = _count_active(atr, df, start)
    n_and = _count_active(comp, df, start)

    assert n_and <= n_sma
    assert n_and <= n_atr


@given(
    returns=st.lists(
        st.floats(
            min_value=-0.03, max_value=0.03, allow_nan=False, allow_infinity=False
        ),
        min_size=80,
        max_size=150,
    ),
    min_slope_bps=st.floats(min_value=0.0, max_value=30.0, allow_nan=False),
    min_atr_bps=st.floats(min_value=0.0, max_value=150.0, allow_nan=False),
)
@settings(max_examples=15, deadline=None)
def test_or_permissivo_em_signal_emission(
    returns: list[float],
    min_slope_bps: float,
    min_atr_bps: float,
) -> None:
    df = _window_from_returns(returns)
    sma = SMASlopeFilter(window=50, min_slope_bps=min_slope_bps)
    atr = ATRRegimeFilter(window=14, min_atr_bps=min_atr_bps)
    comp = CompositeFilter([sma, atr], mode="or")

    start = 51

    n_sma = _count_active(sma, df, start)
    n_atr = _count_active(atr, df, start)
    n_or = _count_active(comp, df, start)

    assert n_or >= n_sma
    assert n_or >= n_atr
