"""Donchian breakout causal — ADR-0011 (long-only) + ADR-0013 (short side opt-in).

Regra (ADR-0011 §"Regra exata", estendida por ADR-0013):

Eventos observáveis (inalterados por ADR-0013):

- **Breakout bullish** quando ``high[t-1] > max(high[t-entry_window-1 : t-1])``.
- **Breakout bearish** quando ``low[t-1] < min(low[t-exit_window-1 : t-1])``.
- Desigualdades estritas; empate exato não é sinal.
- Janela de comparação exclui ``t-1``.
- Warm-up: ``HOLD`` enquanto ``len(window) < max(entry_window, exit_window) + 2``.

Mapeamento de sinal depende de ``long_only`` (ADR-0013):

- ``long_only=True`` (default, ADR-0011 preservado bit-a-bit):
    - bullish → ``ENTER_LONG``
    - bearish → ``EXIT``
    - ambos simultâneos → ``EXIT`` (ordem EXIT→ENTER da ADR-0011)
- ``long_only=False`` (ADR-0013):
    - bullish → ``ENTER_LONG``
    - bearish → ``ENTER_SHORT``
    - ambos simultâneos → ``ENTER_SHORT`` (arbitragem conservadora espelhada;
      a informação cronologicamente posterior é a perda do mínimo)

No modo simétrico não há ``EXIT`` explícito — o fechamento ocorre via reversão,
coordenada pelo engine (ADR-0012, reverse-on-signal, custo duplo).

A estratégia ignora ``window.iloc[-1]`` (barra ``t``) por construção.
Stateless: ``decide(window) -> Signal`` é função pura de ``window`` e parâmetros.
"""

from __future__ import annotations

import pandas as pd

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.base import Strategy


class DonchianBreakoutStrategy(Strategy):
    name = "donchian"

    def __init__(
        self,
        entry_window: int,
        exit_window: int,
        long_only: bool = True,
    ) -> None:
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
        if not isinstance(long_only, bool):
            raise TypeError(
                f"long_only deve ser bool, recebeu {type(long_only).__name__}"
            )
        self.entry_window = entry_window
        self.exit_window = exit_window
        self.long_only = long_only

    def decide(self, window: pd.DataFrame) -> Signal:
        min_bars = max(self.entry_window, self.exit_window) + 2
        if len(window) < min_bars:
            return Signal.HOLD

        highs = window["high"].iloc[:-1]
        lows = window["low"].iloc[:-1]

        ref_high = float(highs.iloc[-1])
        ref_low = float(lows.iloc[-1])

        prior_highs = highs.iloc[-self.entry_window - 1 : -1]
        prior_lows = lows.iloc[-self.exit_window - 1 : -1]

        max_prior_high = float(prior_highs.max())
        min_prior_low = float(prior_lows.min())

        bearish = ref_low < min_prior_low
        bullish = ref_high > max_prior_high

        if self.long_only:
            if bearish:
                return Signal.EXIT
            if bullish:
                return Signal.ENTER_LONG
            return Signal.HOLD

        if bearish:
            return Signal.ENTER_SHORT
        if bullish:
            return Signal.ENTER_LONG
        return Signal.HOLD


__all__ = ["DonchianBreakoutStrategy"]
