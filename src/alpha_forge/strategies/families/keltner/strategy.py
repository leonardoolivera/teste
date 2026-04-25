"""Keltner mean-reversion causal — ADR-0170.

Envelope baseado em EMA(close) ± mult × ATR. Diferencia-se de Bollinger por usar
ATR (range-based, robusto a outliers) em vez de desvio padrão (point-based,
amplifica spikes). Mesma semântica de sinal que Bollinger (ADR-0026 + ADR-0051)
para permitir comparação direta.

Regra (causal, ADR-0030 friendly):

Sejam ``closes = window["close"].iloc[:-1]``, ``highs = window["high"].iloc[:-1]``,
``lows = window["low"].iloc[:-1]``. Barra ``t`` ignorada por construção.

- ``ema_now`` = EMA(closes, span=window_size) usando janela até ``t-1``.
- ``atr_now`` = SMA sobre ``tr`` nas últimas ``atr_period`` barras, onde
  ``tr[i] = max(high[i]-low[i], |high[i]-close[i-1]|, |low[i]-close[i-1]|)``.
- ``upper_now = ema_now + atr_mult × atr_now``
- ``lower_now = ema_now - atr_mult × atr_now``
- Para ``_prev``: mesmo computo aplicado ao slice shift -1.

Sinais edge-triggered:

- **Entrada long**: ``c[t-1] < lower_now`` **e** ``c[t-2] >= lower_prev``.
- **Entrada short** (``long_only=False``): ``c[t-1] > upper_now`` **e** ``c[t-2] <= upper_prev``.
- **Saída (long-only)**: ``c[t-1] >= ema_now`` **e** ``c[t-2] < ema_prev``.
- Ordem: EXIT antes de ENTER.
- Simultaneidade long+short (``long_only=False``): HOLD (ambiguidade mean-rev).
- Warm-up: HOLD enquanto ``len(window) < max(window_size, atr_period) + 3``.
"""

from __future__ import annotations

import pandas as pd

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.base import Strategy


class KeltnerMeanReversionStrategy(Strategy):
    name = "keltner"

    def __init__(
        self,
        window: int,
        atr_period: int,
        atr_mult: float,
        long_only: bool = True,
    ) -> None:
        if not isinstance(window, int) or isinstance(window, bool):
            raise TypeError(
                f"window deve ser int, recebeu {type(window).__name__}"
            )
        if window <= 0:
            raise ValueError(f"window deve ser > 0, recebeu {window}")
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
        self.window = window
        self.atr_period = atr_period
        self.atr_mult = float(atr_mult)
        self.long_only = long_only

    def _atr(self, highs: pd.Series, lows: pd.Series, closes: pd.Series) -> float:
        """SMA(TR, atr_period) terminando em closes.index[-1]."""
        n = self.atr_period
        h = highs.iloc[-n:].to_numpy()
        l = lows.iloc[-n:].to_numpy()
        c_curr = closes.iloc[-n:].to_numpy()
        c_prev = closes.iloc[-n - 1 : -1].to_numpy()
        tr1 = h - l
        tr2 = abs(h - c_prev)
        tr3 = abs(l - c_prev)
        tr = [max(a, b, c) for a, b, c in zip(tr1, tr2, tr3)]
        return sum(tr) / n

    def decide(self, window: pd.DataFrame) -> Signal:
        min_bars = max(self.window, self.atr_period) + 3
        if len(window) < min_bars:
            return Signal.HOLD

        closes = window["close"].iloc[:-1]
        highs = window["high"].iloc[:-1]
        lows = window["low"].iloc[:-1]

        # EMA via pandas.ewm; pegar valor terminal nas janelas now/prev
        ema_series_now = closes.ewm(span=self.window, adjust=False).mean()
        ema_now = float(ema_series_now.iloc[-1])
        ema_prev = float(ema_series_now.iloc[-2])

        atr_now = self._atr(highs, lows, closes)
        atr_prev = self._atr(highs.iloc[:-1], lows.iloc[:-1], closes.iloc[:-1])

        lower_now = ema_now - self.atr_mult * atr_now
        lower_prev = ema_prev - self.atr_mult * atr_prev
        upper_now = ema_now + self.atr_mult * atr_now
        upper_prev = ema_prev + self.atr_mult * atr_prev

        c_tm1 = float(closes.iloc[-1])
        c_tm2 = float(closes.iloc[-2])

        long_entry = c_tm1 < lower_now and c_tm2 >= lower_prev
        short_entry = c_tm1 > upper_now and c_tm2 <= upper_prev

        if self.long_only:
            exit_triggered = c_tm1 >= ema_now and c_tm2 < ema_prev
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


__all__ = ["KeltnerMeanReversionStrategy"]
