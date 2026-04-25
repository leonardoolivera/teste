"""Zscore mean-reversion causal — ADR-0175.

Diferencia de Bollinger por:
- Threshold fixo em desvios-padrão (semântica discreta), não banda absoluta.
- Exit em **zero-crossing** (volta ao z=0), não em volta à mean band.

Regra (causal, ADR-0030 friendly):

Seja ``closes = window["close"].iloc[:-1]``. Barra ``t`` ignorada por construção.

- ``mu_now``, ``sigma_now`` = mean/pstdev sobre ``closes.iloc[-window:]``.
- ``z_now = (close[t-1] - mu_now) / sigma_now``.
- Análogo ``mu_prev``, ``sigma_prev``, ``z_prev = (close[t-2] - mu_prev) / sigma_prev``.

Sinais edge-triggered:

- **Entrada long**: ``z_now < -threshold AND z_prev >= -threshold``
- **Entrada short** (``long_only=False``): ``z_now > +threshold AND z_prev <= +threshold``
- **Exit (long-only)**: ``z_now >= 0 AND z_prev < 0`` (zero-crossing positivo)
- Simetria short: reverse-on-signal (ADR-0012/0051) fecha posição em signal oposto
- Simultaneidade long+short → HOLD
- Warm-up: HOLD enquanto ``len(window) < window_size + 3``
- sigma=0 (degenerado): HOLD
"""

from __future__ import annotations

import pandas as pd

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.base import Strategy


class ZScoreMeanReversionStrategy(Strategy):
    name = "zscore"

    def __init__(
        self,
        window: int,
        threshold: float,
        long_only: bool = True,
    ) -> None:
        if not isinstance(window, int) or isinstance(window, bool):
            raise TypeError(
                f"window deve ser int, recebeu {type(window).__name__}"
            )
        if window <= 0:
            raise ValueError(f"window deve ser > 0, recebeu {window}")
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
            raise TypeError(
                f"threshold deve ser float, recebeu {type(threshold).__name__}"
            )
        if threshold <= 0:
            raise ValueError(f"threshold deve ser > 0, recebeu {threshold}")
        if not isinstance(long_only, bool):
            raise TypeError(
                f"long_only deve ser bool, recebeu {type(long_only).__name__}"
            )
        self.window = window
        self.threshold = float(threshold)
        self.long_only = long_only

    def decide(self, window: pd.DataFrame) -> Signal:
        min_bars = self.window + 3
        if len(window) < min_bars:
            return Signal.HOLD

        closes = window["close"].iloc[:-1]

        now_slice = closes.iloc[-self.window :]
        prev_slice = closes.iloc[-self.window - 1 : -1]

        mu_now = float(now_slice.mean())
        sigma_now = float(now_slice.std(ddof=0))
        mu_prev = float(prev_slice.mean())
        sigma_prev = float(prev_slice.std(ddof=0))

        if sigma_now == 0.0 or sigma_prev == 0.0:
            return Signal.HOLD

        c_tm1 = float(closes.iloc[-1])
        c_tm2 = float(closes.iloc[-2])

        z_now = (c_tm1 - mu_now) / sigma_now
        z_prev = (c_tm2 - mu_prev) / sigma_prev

        long_entry = z_now < -self.threshold and z_prev >= -self.threshold
        short_entry = z_now > self.threshold and z_prev <= self.threshold

        if self.long_only:
            exit_triggered = z_now >= 0.0 and z_prev < 0.0
            if exit_triggered:
                return Signal.EXIT
            if long_entry:
                return Signal.ENTER_LONG
            return Signal.HOLD

        if long_entry and short_entry:
            return Signal.HOLD
        if long_entry:
            return Signal.ENTER_LONG
        if short_entry:
            return Signal.ENTER_SHORT
        return Signal.HOLD


__all__ = ["ZScoreMeanReversionStrategy"]
