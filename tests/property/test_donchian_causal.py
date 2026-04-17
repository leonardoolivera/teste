"""Property-based test de causalidade do DonchianBreakoutStrategy (ADR-0011).

Propriedade: sinal em `t` é função pura de `prices[:t+1]`. Mutação em barras
futuras (OHLC completo, não só um campo) não altera o sinal em `t`.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from alpha_forge.strategies.families.donchian import DonchianBreakoutStrategy


def _ohlc_from_closes(closes: np.ndarray) -> pd.DataFrame:
    highs = closes * 1.02
    lows = closes * 0.98
    opens = closes
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    idx = pd.date_range(start=start, periods=len(closes), freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": np.ones(len(closes)),
        },
        index=idx,
    )


@given(
    closes=st.lists(
        st.floats(min_value=1.0, max_value=1_000.0, allow_nan=False, allow_infinity=False),
        min_size=15,
        max_size=60,
    ),
    t_frac=st.floats(min_value=0.3, max_value=0.9),
    perturb=st.floats(min_value=-500.0, max_value=500.0, allow_nan=False, allow_infinity=False),
    perturb_offset=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=80, deadline=None)
def test_sinal_em_t_independe_do_futuro_ohlc_completo(
    closes: list[float],
    t_frac: float,
    perturb: float,
    perturb_offset: int,
) -> None:
    n = len(closes)
    arr = np.array(closes, dtype=float)
    df_original = _ohlc_from_closes(arr)

    strat = DonchianBreakoutStrategy(entry_window=5, exit_window=3)

    t = max(7, min(n - 1, int(n * t_frac)))

    future_idx = t + perturb_offset
    if future_idx >= n:
        return

    arr_mutated = arr.copy()
    new_value = arr_mutated[future_idx] + perturb
    if new_value <= 0:
        new_value = abs(new_value) + 1.0
    arr_mutated[future_idx] = new_value
    df_mutated = _ohlc_from_closes(arr_mutated)

    mutated_full = df_mutated.copy()
    mutated_full.iloc[future_idx, mutated_full.columns.get_loc("high")] = new_value * 2.0
    mutated_full.iloc[future_idx, mutated_full.columns.get_loc("low")] = new_value * 0.1
    mutated_full.iloc[future_idx, mutated_full.columns.get_loc("open")] = new_value * 1.5

    sig_original = strat.decide(df_original.iloc[: t + 1])
    sig_mutated = strat.decide(mutated_full.iloc[: t + 1])

    assert sig_original == sig_mutated, (
        f"sinal em t={t} mudou ao perturbar barra futura t+{perturb_offset}: "
        f"{sig_original} → {sig_mutated}"
    )
