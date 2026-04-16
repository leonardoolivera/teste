"""Gerador determinístico de OHLCV sintético para o núcleo mínimo.

Existe para permitir que o pipeline rode end-to-end sem depender de download real.
Série previsível, pequena, com drift e ruído reproduzíveis via seed.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd


TIMEFRAME_DELTAS: dict[str, timedelta] = {
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "1d": timedelta(days=1),
}


def generate_ohlcv(
    *,
    start: datetime,
    periods: int,
    timeframe: str = "1h",
    initial_price: float = 100.0,
    drift: float = 0.0002,
    volatility: float = 0.01,
    seed: int = 42,
) -> pd.DataFrame:
    """Gera DataFrame OHLCV determinístico indexado por timestamp UTC.

    Colunas: ``open, high, low, close, volume``.
    Index: ``DatetimeIndex`` UTC-aware, com nome ``timestamp``.
    """
    if timeframe not in TIMEFRAME_DELTAS:
        raise ValueError(f"timeframe '{timeframe}' não suportado pelo sintético")
    if periods <= 0:
        raise ValueError("periods deve ser > 0")
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)

    rng = np.random.default_rng(seed)
    step = TIMEFRAME_DELTAS[timeframe]
    index = pd.DatetimeIndex(
        [start + i * step for i in range(periods)],
        name="timestamp",
        tz="UTC",
    )

    returns = rng.normal(loc=drift, scale=volatility, size=periods)
    close = initial_price * np.exp(np.cumsum(returns))
    open_ = np.empty(periods)
    open_[0] = initial_price
    open_[1:] = close[:-1]

    intrabar = rng.uniform(0.0, volatility, size=periods)
    high = np.maximum(open_, close) * (1.0 + intrabar)
    low = np.minimum(open_, close) * (1.0 - intrabar)
    volume = rng.uniform(100.0, 1000.0, size=periods)

    return pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        },
        index=index,
    )
