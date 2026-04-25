"""Property-based test de causalidade da RSIMeanReversionStrategy (ADR-0027).

Propriedade verificada: o sinal em ``t`` é função pura de ``prices[:t]`` — a
estratégia ignora ``window.iloc[-1]`` por construção. Qualquer mutação na
barra ``t`` (OHLC completo) ou em qualquer barra futura não pode alterar o
sinal em ``t``.

Gerador respeita invariantes mínimos de OHLC:
  - ``high >= max(open, close)``
  - ``low <= min(open, close)``
  - ``high >= low``
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

from alpha_forge.strategies.families.rsi import RSIMeanReversionStrategy


PERIOD = 4
OVERSOLD = 30.0
OVERBOUGHT = 70.0
MIN_BARS = PERIOD + 3  # 7


def _index(n: int) -> pd.DatetimeIndex:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return pd.date_range(start=start, periods=n, freq="1h", tz="UTC")


@st.composite
def ohlc_bars(draw: st.DrawFn, min_size: int = 20, max_size: int = 80) -> pd.DataFrame:
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    rows: list[dict[str, float]] = []
    for _ in range(n):
        o = draw(st.floats(min_value=1.0, max_value=1_000.0, allow_nan=False, allow_infinity=False))
        c = draw(st.floats(min_value=1.0, max_value=1_000.0, allow_nan=False, allow_infinity=False))
        spread_up = draw(st.floats(min_value=0.0, max_value=50.0, allow_nan=False, allow_infinity=False))
        spread_down = draw(st.floats(min_value=0.0, max_value=50.0, allow_nan=False, allow_infinity=False))
        high = max(o, c) + spread_up
        low = max(0.01, min(o, c) - spread_down)
        low = min(low, min(o, c))
        rows.append({"open": o, "high": high, "low": low, "close": c, "volume": 1.0})
    df = pd.DataFrame(rows, index=_index(n))
    assert (df["high"] >= df[["open", "close"]].max(axis=1)).all()
    assert (df["low"] <= df[["open", "close"]].min(axis=1)).all()
    assert (df["high"] >= df["low"]).all()
    return df


@given(
    df=ohlc_bars(min_size=MIN_BARS + 5, max_size=60),
    t_frac=st.floats(min_value=0.3, max_value=0.9),
    perturb_offset=st.integers(min_value=0, max_value=10),
    new_high=st.floats(min_value=0.5, max_value=5_000.0, allow_nan=False, allow_infinity=False),
    new_low=st.floats(min_value=0.1, max_value=4_999.0, allow_nan=False, allow_infinity=False),
    new_close=st.floats(min_value=0.5, max_value=5_000.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100, deadline=None)
def test_sinal_em_t_independe_do_futuro_e_da_barra_t(
    df: pd.DataFrame,
    t_frac: float,
    perturb_offset: int,
    new_high: float,
    new_low: float,
    new_close: float,
) -> None:
    n = len(df)
    strat = RSIMeanReversionStrategy(
        period=PERIOD, oversold=OVERSOLD, overbought=OVERBOUGHT
    )

    t = max(MIN_BARS - 1, min(n - 1, int(n * t_frac)))

    sig_original = strat.decide(df.iloc[: t + 1])

    target_idx = t + perturb_offset
    if target_idx >= n:
        sig_again = strat.decide(df.iloc[: t + 1])
        assert sig_again == sig_original
        return

    h = max(new_high, new_close) + 0.01
    low = min(new_low, new_close) - 0.01
    if low <= 0:
        low = 0.01
    c = max(0.01, min(new_close, h - 1e-9))
    o = max(0.01, min(new_close, h - 1e-9))

    mutated = df.copy()
    mutated_idx = mutated.index[target_idx]
    mutated.at[mutated_idx, "open"] = o
    mutated.at[mutated_idx, "high"] = h
    mutated.at[mutated_idx, "low"] = low
    mutated.at[mutated_idx, "close"] = c

    sig_mutated = strat.decide(mutated.iloc[: t + 1])

    assert sig_original == sig_mutated, (
        f"sinal em t={t} mudou após mutar barra em t+{perturb_offset}: "
        f"{sig_original} → {sig_mutated}"
    )
