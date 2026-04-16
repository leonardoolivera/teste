"""Moving average crossover causal (long-only) — ADR-0008.

SMA curta × SMA longa sobre a coluna ``close``. Sinal é função pura de
``prices[:t+1]``: nenhum estado interno, nenhum acesso a futuro.

Regras (ADR-0008 §4):

- ``ENTER_LONG``: ``short[t] > long[t]`` e ``short[t-1] <= long[t-1]``.
- ``EXIT``:      ``short[t] < long[t]`` e ``short[t-1] >= long[t-1]``.
- Igualdade exata, warm-up, qualquer outro estado → ``HOLD``.

Warm-up (ADR-0008 §5): ``HOLD`` enquanto ``len(window) < long_window + 1``.
Estado esperado, não erro. Sem fillna, sem preenchimento mágico, sem fallback.
"""

from __future__ import annotations

import pandas as pd

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.base import Strategy


class MovingAverageCrossoverStrategy(Strategy):
    name = "ma_crossover"

    def __init__(self, short_window: int, long_window: int) -> None:
        if not isinstance(short_window, int) or isinstance(short_window, bool):
            raise TypeError(
                f"short_window deve ser int, recebeu {type(short_window).__name__}"
            )
        if not isinstance(long_window, int) or isinstance(long_window, bool):
            raise TypeError(
                f"long_window deve ser int, recebeu {type(long_window).__name__}"
            )
        if short_window <= 0:
            raise ValueError(f"short_window deve ser > 0, recebeu {short_window}")
        if long_window <= 0:
            raise ValueError(f"long_window deve ser > 0, recebeu {long_window}")
        if short_window >= long_window:
            raise ValueError(
                f"short_window ({short_window}) deve ser estritamente menor que "
                f"long_window ({long_window})"
            )
        self.short_window = short_window
        self.long_window = long_window

    def decide(self, window: pd.DataFrame) -> Signal:
        if len(window) < self.long_window + 1:
            return Signal.HOLD

        closes = window["close"]
        short_now = float(closes.iloc[-self.short_window :].mean())
        long_now = float(closes.iloc[-self.long_window :].mean())
        short_prev = float(closes.iloc[-self.short_window - 1 : -1].mean())
        long_prev = float(closes.iloc[-self.long_window - 1 : -1].mean())

        if short_now > long_now and short_prev <= long_prev:
            return Signal.ENTER_LONG
        if short_now < long_now and short_prev >= long_prev:
            return Signal.EXIT
        return Signal.HOLD


__all__ = ["MovingAverageCrossoverStrategy"]
