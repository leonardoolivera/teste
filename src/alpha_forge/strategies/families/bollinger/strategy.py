"""Bollinger mean-reversion causal — ADR-0026 (long-only) + ADR-0051 (short side).

Regra long-only (ADR-0026 §"Regra exata"):

Seja ``closes = window["close"].iloc[:-1]`` (barra ``t`` ignorada por construção).

- ``mu_now``, ``sigma_now`` = média/pstdev sobre ``closes.iloc[-window_size:]``.
- ``mu_prev``, ``sigma_prev`` = média/pstdev sobre ``closes.iloc[-window_size-1:-1]``.

Sinais edge-triggered (cruzamento estrito; ``>=`` / ``<``):

- **Entrada long** quando ``close[t-1] < lower_now`` **e** ``close[t-2] >= lower_prev``.
- **Saída (long-only)** quando ``close[t-1] >= mu_now`` **e** ``close[t-2] < mu_prev``.
- Ordem: EXIT antes de ENTER_LONG.
- Warm-up: ``HOLD`` enquanto ``len(window) < window_size + 3``.

Regra short side (ADR-0051) — ativada com ``long_only=False``:

- **Entrada short** quando ``close[t-1] > upper_now`` **e** ``close[t-2] <= upper_prev``.
- Sem EXIT explícito em modo simétrico — ADR-0012 reverse-on-signal fecha posição.
- Ambos long_entry e short_entry simultâneos → ``HOLD`` (ambiguidade mean-rev; ADR-0051).
"""

from __future__ import annotations

import pandas as pd

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.base import Strategy


class BollingerMeanReversionStrategy(Strategy):
    name = "bollinger"

    def __init__(
        self,
        window: int,
        num_std: float,
        long_only: bool = True,
    ) -> None:
        if not isinstance(window, int) or isinstance(window, bool):
            raise TypeError(
                f"window deve ser int, recebeu {type(window).__name__}"
            )
        if window <= 0:
            raise ValueError(f"window deve ser > 0, recebeu {window}")
        if isinstance(num_std, bool) or not isinstance(num_std, (int, float)):
            raise TypeError(
                f"num_std deve ser float, recebeu {type(num_std).__name__}"
            )
        if num_std <= 0:
            raise ValueError(f"num_std deve ser > 0, recebeu {num_std}")
        if not isinstance(long_only, bool):
            raise TypeError(
                f"long_only deve ser bool, recebeu {type(long_only).__name__}"
            )
        self.window = window
        self.num_std = float(num_std)
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

        lower_now = mu_now - self.num_std * sigma_now
        lower_prev = mu_prev - self.num_std * sigma_prev
        upper_now = mu_now + self.num_std * sigma_now
        upper_prev = mu_prev + self.num_std * sigma_prev

        c_tm1 = float(closes.iloc[-1])
        c_tm2 = float(closes.iloc[-2])

        long_entry = c_tm1 < lower_now and c_tm2 >= lower_prev
        short_entry = c_tm1 > upper_now and c_tm2 <= upper_prev

        if self.long_only:
            exit_triggered = c_tm1 >= mu_now and c_tm2 < mu_prev
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


__all__ = ["BollingerMeanReversionStrategy"]
