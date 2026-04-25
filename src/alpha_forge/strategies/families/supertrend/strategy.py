"""SuperTrend trend-follow causal — ADR-0193.

ATR-based trailing band que flipa entre trend up/down em breakout. Ortogonal
a BB/RSI (MR contra extremos). Primeiro engine trend-follow primário no AF.

Regra (causal, ADR-0030 friendly):

Sejam ``highs = window["high"].iloc[:-1]``, ``lows = window["low"].iloc[:-1]``,
``closes = window["close"].iloc[:-1]``. Barra ``t`` ignorada por construção.

Para cada ``i`` em ``[atr_period, ..., len-1]``:
- ``hl2[i] = (high[i] + low[i]) / 2``
- ``tr[i] = max(high[i]-low[i], |high[i]-close[i-1]|, |low[i]-close[i-1]|)``
- ``atr[i] = SMA(tr, atr_period)`` terminando em ``i``
- ``upper_band[i] = hl2[i] + atr_mult * atr[i]``
- ``lower_band[i] = hl2[i] - atr_mult * atr[i]``
- ``f_upper[i] = min(upper_band[i], f_upper[i-1])`` se ``close[i-1] <= f_upper[i-1]``,
  senão ``upper_band[i]``.
- ``f_lower[i] = max(lower_band[i], f_lower[i-1])`` se ``close[i-1] >= f_lower[i-1]``,
  senão ``lower_band[i]``.
- Trend:
  * ``trend[i] = -1`` se ``trend[i-1] == +1 AND close[i] < f_lower[i]``
  * ``trend[i] = +1`` se ``trend[i-1] == -1 AND close[i] > f_upper[i]``
  * senão ``trend[i] = trend[i-1]``

Seed: ``trend[atr_period] = +1`` (arbitrário, sem look-ahead — valor inicial
irrelevante após primeiro flip).

Sinais edge-triggered usando ``trend_now = trend[-1]``, ``trend_prev = trend[-2]``:

- **Entrada long**: flip up (``trend_now == +1 AND trend_prev == -1``)
- **Entrada short** (``long_only=False``): flip down (``trend_now == -1 AND trend_prev == +1``)
- **Saída (long-only)**: flip down
- **Bidirectional**: reverse-on-signal (ADR-0011) via Backtester
- **Warm-up**: HOLD enquanto ``len(window) < atr_period + 5``
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.base import Strategy


class SuperTrendStrategy(Strategy):
    name = "supertrend"

    def __init__(
        self,
        atr_period: int,
        atr_mult: float,
        long_only: bool = False,
    ) -> None:
        if not isinstance(atr_period, int) or isinstance(atr_period, bool):
            raise TypeError(
                f"atr_period deve ser int, recebeu {type(atr_period).__name__}"
            )
        if atr_period <= 0:
            raise ValueError(f"atr_period deve ser > 0, recebeu {atr_period}")
        if isinstance(atr_mult, bool) or not isinstance(atr_mult, (int, float)):
            raise TypeError(
                f"atr_mult deve ser float, recebeu {type(atr_mult).__name__}"
            )
        if atr_mult <= 0:
            raise ValueError(f"atr_mult deve ser > 0, recebeu {atr_mult}")
        if not isinstance(long_only, bool):
            raise TypeError(
                f"long_only deve ser bool, recebeu {type(long_only).__name__}"
            )
        self.atr_period = atr_period
        self.atr_mult = float(atr_mult)
        self.long_only = long_only

    def _compute_trend(
        self,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
    ) -> np.ndarray:
        n = len(closes)
        trend = np.zeros(n, dtype=np.int8)
        if n < self.atr_period + 2:
            return trend

        # TR — requer close[i-1] para i>=1
        tr = np.zeros(n)
        for i in range(1, n):
            tr[i] = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1]),
            )

        # ATR (SMA) — a partir de i = atr_period (janela [i-atr_period+1 .. i])
        atr = np.zeros(n)
        p = self.atr_period
        for i in range(p, n):
            atr[i] = tr[i - p + 1 : i + 1].mean()

        hl2 = (highs + lows) / 2.0
        upper = hl2 + self.atr_mult * atr
        lower = hl2 - self.atr_mult * atr

        f_upper = np.zeros(n)
        f_lower = np.zeros(n)
        f_upper[p] = upper[p]
        f_lower[p] = lower[p]
        trend[p] = 1  # seed arbitrário

        for i in range(p + 1, n):
            # final upper
            if upper[i] < f_upper[i - 1] or closes[i - 1] > f_upper[i - 1]:
                f_upper[i] = upper[i]
            else:
                f_upper[i] = f_upper[i - 1]
            # final lower
            if lower[i] > f_lower[i - 1] or closes[i - 1] < f_lower[i - 1]:
                f_lower[i] = lower[i]
            else:
                f_lower[i] = f_lower[i - 1]
            # trend
            if trend[i - 1] == 1 and closes[i] < f_lower[i]:
                trend[i] = -1
            elif trend[i - 1] == -1 and closes[i] > f_upper[i]:
                trend[i] = 1
            else:
                trend[i] = trend[i - 1]

        return trend

    def decide(self, window: pd.DataFrame) -> Signal:
        min_bars = self.atr_period + 5
        if len(window) < min_bars:
            return Signal.HOLD

        highs = window["high"].iloc[:-1].to_numpy(dtype=float)
        lows = window["low"].iloc[:-1].to_numpy(dtype=float)
        closes = window["close"].iloc[:-1].to_numpy(dtype=float)

        trend = self._compute_trend(highs, lows, closes)

        if len(trend) < 2:
            return Signal.HOLD

        trend_now = int(trend[-1])
        trend_prev = int(trend[-2])

        flip_up = trend_now == 1 and trend_prev == -1
        flip_down = trend_now == -1 and trend_prev == 1

        if self.long_only:
            if flip_down:
                return Signal.EXIT
            if flip_up:
                return Signal.ENTER_LONG
            return Signal.HOLD

        if flip_up:
            return Signal.ENTER_LONG
        if flip_down:
            return Signal.ENTER_SHORT
        return Signal.HOLD


__all__ = ["SuperTrendStrategy"]
