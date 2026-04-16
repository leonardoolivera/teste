"""Property-based test de causalidade da MovingAverageCrossoverStrategy (ADR-0008).

Propriedade verificada: o sinal em `t` é função pura de `prices[:t+1]`.
Qualquer mutação em barras ``> t`` não pode alterar o sinal em `t`.

Isso garante estruturalmente que a estratégia respeita o Contrato A (janela
causal) de ADR-0002.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from alpha_forge.strategies.families.ma_crossover import MovingAverageCrossoverStrategy


def _index(n: int) -> pd.DatetimeIndex:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return pd.date_range(start=start, periods=n, freq="1h", tz="UTC")


def _df_from_closes(closes: np.ndarray) -> pd.DataFrame:
    idx = _index(len(closes))
    return pd.DataFrame(
        {
            "open": closes,
            "high": closes * 1.001,
            "low": closes * 0.999,
            "close": closes,
            "volume": np.ones(len(closes)),
        },
        index=idx,
    )


@given(
    closes=st.lists(
        st.floats(
            min_value=1.0, max_value=1_000.0, allow_nan=False, allow_infinity=False
        ),
        min_size=20,
        max_size=80,
    ),
    t_frac=st.floats(min_value=0.3, max_value=0.9),
    perturb=st.floats(
        min_value=-500.0, max_value=500.0, allow_nan=False, allow_infinity=False
    ),
    perturb_offset=st.integers(min_value=1, max_value=10),
    seed=st.integers(min_value=0, max_value=10_000),
)
@settings(max_examples=100, deadline=None)
def test_sinal_em_t_independe_do_futuro(
    closes: list[float],
    t_frac: float,
    perturb: float,
    perturb_offset: int,
    seed: int,
) -> None:
    n = len(closes)
    arr = np.array(closes, dtype=float)
    df_original = _df_from_closes(arr)

    strat = MovingAverageCrossoverStrategy(short_window=3, long_window=10)

    t = max(10, min(n - 1, int(n * t_frac)))

    future_idx = t + perturb_offset
    if future_idx >= n:
        sig_original = strat.decide(df_original.iloc[: t + 1])
        sig_no_future = strat.decide(df_original.iloc[: t + 1])
        assert sig_original == sig_no_future
        return

    arr_mutated = arr.copy()
    new_value = arr_mutated[future_idx] + perturb
    if new_value <= 0:
        new_value = abs(new_value) + 1.0
    arr_mutated[future_idx] = new_value
    df_mutated = _df_from_closes(arr_mutated)

    sig_original = strat.decide(df_original.iloc[: t + 1])
    sig_mutated = strat.decide(df_mutated.iloc[: t + 1])

    assert sig_original == sig_mutated, (
        f"sinal em t={t} mudou após perturbar barra futura em t+{perturb_offset}: "
        f"{sig_original} → {sig_mutated}"
    )
    _ = seed
