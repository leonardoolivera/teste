"""Donchian breakout causal (long-only) — ADR-0011.

Implementação estrita do contrato:

- Entrada long em ``t`` quando ``high[t-1] > max(high[t-entry_window-1 : t-1])``.
- Saída em ``t`` quando ``low[t-1] < min(low[t-exit_window-1 : t-1])``.
- Ordem de avaliação: saída antes da entrada. Ambas usam estritamente ``>`` / ``<``.
- Warm-up: ``HOLD`` enquanto ``len(window) < max(entry_window, exit_window) + 2``.
- Long-only. Universo de saída: ``ENTER_LONG``, ``EXIT``, ``HOLD``.
- Stateless. Ignora ``window.iloc[-1]`` por construção (mesmo que o engine já
  garanta causalidade).

Nenhum default no construtor. Defaults (20/10) vivem apenas na CLI.
"""

from __future__ import annotations

import pandas as pd

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.base import Strategy


class DonchianBreakoutStrategy(Strategy):
    name = "donchian"

    def __init__(self, entry_window: int, exit_window: int) -> None:
        if not isinstance(entry_window, int) or isinstance(entry_window, bool):
            raise TypeError(
                f"entry_window deve ser int, recebeu {type(entry_window).__name__}"
            )
        if not isinstance(exit_window, int) or isinstance(exit_window, bool):
            raise TypeError(
                f"exit_window deve ser int, recebeu {type(exit_window).__name__}"
            )
        if entry_window <= 0:
            raise ValueError(f"entry_window deve ser > 0, recebeu {entry_window}")
        if exit_window <= 0:
            raise ValueError(f"exit_window deve ser > 0, recebeu {exit_window}")
        self.entry_window = entry_window
        self.exit_window = exit_window

    def decide(self, window: pd.DataFrame) -> Signal:
        warmup = max(self.entry_window, self.exit_window) + 2
        if len(window) < warmup:
            return Signal.HOLD

        highs = window["high"]
        lows = window["low"]

        high_tm1 = float(highs.iloc[-2])
        low_tm1 = float(lows.iloc[-2])

        entry_window_max = float(
            highs.iloc[-self.entry_window - 2 : -2].max()
        )
        exit_window_min = float(
            lows.iloc[-self.exit_window - 2 : -2].min()
        )

        if low_tm1 < exit_window_min:
            return Signal.EXIT
        if high_tm1 > entry_window_max:
            return Signal.ENTER_LONG
        return Signal.HOLD


__all__ = ["DonchianBreakoutStrategy"]
