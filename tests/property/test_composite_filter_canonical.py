"""Property-based: ``canonical_string`` de ``CompositeFilter`` é comutativo (ADR-0023).

`canonical_string(CompositeFilter([f1, f2], mode))` deve ser idêntico a
`canonical_string(CompositeFilter([f2, f1], mode))` — filtros internos
são ordenados lexicograficamente na serialização.

Também testa **roundtrip**: `parse_spec(canonical_string(f)) == f`
(preserva modo e conjunto de filtros internos).
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from alpha_forge.regimes import (
    ATRRegimeFilter,
    CompositeFilter,
    SMASlopeFilter,
    canonical_string,
    parse_spec,
)


@given(
    sma_window=st.integers(min_value=10, max_value=100),
    min_slope_bps=st.floats(min_value=0.0, max_value=50.0, allow_nan=False),
    atr_window=st.integers(min_value=5, max_value=50),
    min_atr_bps=st.floats(min_value=0.0, max_value=200.0, allow_nan=False),
    mode=st.sampled_from(["and", "or"]),
)
@settings(max_examples=30, deadline=None)
def test_canonical_string_commutative(
    sma_window: int,
    min_slope_bps: float,
    atr_window: int,
    min_atr_bps: float,
    mode: str,
) -> None:
    sma = SMASlopeFilter(window=sma_window, min_slope_bps=min_slope_bps)
    atr = ATRRegimeFilter(window=atr_window, min_atr_bps=min_atr_bps)

    c1 = CompositeFilter([sma, atr], mode=mode)  # type: ignore[arg-type]
    c2 = CompositeFilter([atr, sma], mode=mode)  # type: ignore[arg-type]

    s1 = canonical_string(c1)
    s2 = canonical_string(c2)
    assert s1 == s2

    # Roundtrip: parse → canonical → parse produz mesma string
    parsed = parse_spec(s1)
    assert canonical_string(parsed) == s1

    # Mode preservado
    assert parsed.mode == mode  # type: ignore[union-attr]
