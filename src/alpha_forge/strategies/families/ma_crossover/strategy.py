"""Moving average crossover causal — ADR-0008 (long-only) e ADR-0012 (short opt-in).

SMA curta × SMA longa sobre a coluna ``close``. Sinal é função pura de
``prices[:t+1]``: nenhum estado interno, nenhum acesso a futuro.

Regras (ADR-0008 §4, estendido por ADR-0012):

- Cross-up: ``short[t] > long[t]`` e ``short[t-1] <= long[t-1]``.
- Cross-down: ``short[t] < long[t]`` e ``short[t-1] >= long[t-1]``.

Mapeamento de sinal depende de ``long_only`` (ADR-0012):

- ``long_only=True``  (default, ADR-0008): cross-up → ENTER_LONG; cross-down → EXIT.
- ``long_only=False`` (ADR-0012):          cross-up → ENTER_LONG; cross-down → ENTER_SHORT.

Reversão de posição no modo simétrico (estar comprado e receber ENTER_SHORT,
ou vice-versa) é **responsabilidade do engine** (reverse-on-signal,
ADR-0012): a estratégia emite um único sinal por barra.

Igualdade exata, warm-up, qualquer outro estado → ``HOLD``.

Warm-up (ADR-0008 §5): ``HOLD`` enquanto ``len(window) < long_window + 1``.
Estado esperado, não erro. Sem fillna, sem preenchimento mágico, sem fallback.
"""

from __future__ import annotations

import pandas as pd

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.base import Strategy


class MovingAverageCrossoverStrategy(Strategy):
    name = "ma_crossover"

    def __init__(
        self,
        short_window: int,
        long_window: int,
        long_only: bool = True,
    ) -> None:
        if not isinstance(short_window, int) or isinstance(short_window, bool):
            raise TypeError(
                f"short_window deve ser int, recebeu {type(short_window).__name__}"
            )
        if not isinstance(long_window, int) or isinstance(long_window, bool):
            raise TypeError(
                f"long_window deve ser int, recebeu {type(long_window).__name__}"
            )
        if not isinstance(long_only, bool):
            raise TypeError(
                f"long_only deve ser bool, recebeu {type(long_only).__name__}"
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
        self.long_only = long_only

    def decide(self, window: pd.DataFrame) -> Signal:
        if len(window) < self.long_window + 1:
            return Signal.HOLD

        closes = window["close"]
        short_now = float(closes.iloc[-self.short_window :].mean())
        long_now = float(closes.iloc[-self.long_window :].mean())
        short_prev = float(closes.iloc[-self.short_window - 1 : -1].mean())
        long_prev = float(closes.iloc[-self.long_window - 1 : -1].mean())

        cross_up = short_now > long_now and short_prev <= long_prev
        cross_down = short_now < long_now and short_prev >= long_prev

        if cross_up:
            return Signal.ENTER_LONG
        if cross_down:
            return Signal.ENTER_SHORT if not self.long_only else Signal.EXIT
        return Signal.HOLD


__all__ = ["MovingAverageCrossoverStrategy"]
