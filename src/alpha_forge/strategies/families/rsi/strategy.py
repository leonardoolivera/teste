"""RSI mean-reversion causal — ADR-0027 (long-only) + ADR-0051 (short side).

Regra long-only (ADR-0027 §"Regra exata"):

- **Entrada long** quando ``rsi_now < oversold`` **e** ``rsi_prev >= oversold``.
- **Saída (long-only)** quando ``rsi_now >= 50.0`` **e** ``rsi_prev < 50.0``.
- Ordem: EXIT antes de ENTER_LONG.
- Warm-up: ``HOLD`` enquanto ``len(window) < period + 3``.

Regra short side (ADR-0051) — ativada com ``long_only=False``:

- **Entrada short** quando ``rsi_now > overbought`` **e** ``rsi_prev <= overbought``.
- Sem EXIT explícito em modo simétrico — ADR-0012 reverse-on-signal fecha posição.
- Ambos long_entry e short_entry simultâneos é impossível por construção
  (``oversold < 50 < overbought``). Assert defensivo.

SMA smoothing (não Wilder EMA) — ADR-0027 §"Por que SMA".
"""

from __future__ import annotations

import pandas as pd

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.base import Strategy


class RSIMeanReversionStrategy(Strategy):
    name = "rsi"

    def __init__(
        self,
        period: int,
        oversold: float,
        overbought: float,
        long_only: bool = True,
    ) -> None:
        if not isinstance(period, int) or isinstance(period, bool):
            raise TypeError(
                f"period deve ser int, recebeu {type(period).__name__}"
            )
        if period <= 0:
            raise ValueError(f"period deve ser > 0, recebeu {period}")
        if isinstance(oversold, bool) or not isinstance(oversold, (int, float)):
            raise TypeError(
                f"oversold deve ser float, recebeu {type(oversold).__name__}"
            )
        if not (0 < oversold < 50):
            raise ValueError(
                f"oversold deve estar em (0, 50), recebeu {oversold}"
            )
        if isinstance(overbought, bool) or not isinstance(overbought, (int, float)):
            raise TypeError(
                f"overbought deve ser float, recebeu {type(overbought).__name__}"
            )
        if not (50 < overbought < 100):
            raise ValueError(
                f"overbought deve estar em (50, 100), recebeu {overbought}"
            )
        if not isinstance(long_only, bool):
            raise TypeError(
                f"long_only deve ser bool, recebeu {type(long_only).__name__}"
            )
        self.period = period
        self.oversold = float(oversold)
        self.overbought = float(overbought)
        self.long_only = long_only

    def decide(self, window: pd.DataFrame) -> Signal:
        min_bars = self.period + 3
        if len(window) < min_bars:
            return Signal.HOLD

        closes = window["close"].iloc[:-1]
        deltas = closes.diff().iloc[1:]

        gains = deltas.where(deltas > 0, 0.0)
        losses = (-deltas).where(deltas < 0, 0.0)

        gains_now = gains.iloc[-self.period :]
        losses_now = losses.iloc[-self.period :]
        gains_prev = gains.iloc[-self.period - 1 : -1]
        losses_prev = losses.iloc[-self.period - 1 : -1]

        avg_gain_now = float(gains_now.mean())
        avg_loss_now = float(losses_now.mean())
        avg_gain_prev = float(gains_prev.mean())
        avg_loss_prev = float(losses_prev.mean())

        rsi_now = _rsi_from_avgs(avg_gain_now, avg_loss_now)
        rsi_prev = _rsi_from_avgs(avg_gain_prev, avg_loss_prev)

        long_entry = rsi_now < self.oversold and rsi_prev >= self.oversold
        short_entry = rsi_now > self.overbought and rsi_prev <= self.overbought

        if self.long_only:
            exit_triggered = rsi_now >= 50.0 and rsi_prev < 50.0
            if exit_triggered:
                return Signal.EXIT
            if long_entry:
                return Signal.ENTER_LONG
            return Signal.HOLD

        assert not (long_entry and short_entry), (
            f"RSI long+short simultâneo impossível: rsi_now={rsi_now}, "
            f"oversold={self.oversold}, overbought={self.overbought} (ADR-0051)"
        )
        if long_entry:
            return Signal.ENTER_LONG
        if short_entry:
            return Signal.ENTER_SHORT
        return Signal.HOLD


def _rsi_from_avgs(avg_gain: float, avg_loss: float) -> float:
    if avg_loss == 0.0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + rs)


__all__ = ["RSIMeanReversionStrategy"]
