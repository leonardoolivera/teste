"""Estratégia dummy — existe apenas para validar o fluxo end-to-end.

NÃO é uma estratégia "séria". Regra propositalmente ingênua sobre as duas
últimas barras:

  - close subiu → ENTER_LONG
  - close caiu → ENTER_SHORT
  - empate → HOLD

Nenhum parâmetro, nenhum estado, nenhuma esperteza. Usa apenas
``window.iloc[-1]`` e ``window.iloc[-2]`` — causalidade trivial de verificar.
Trocas de direção são resolvidas pelo engine, que executa `EXIT` antes de uma
nova entrada quando o sinal chegar via `EXIT`/re-entrada; aqui o objetivo é
só provar o pipeline.
"""

from __future__ import annotations

import pandas as pd

from alpha_forge.backtest.schemas import Signal
from alpha_forge.strategies.base import Strategy


class DummyAlternatingStrategy(Strategy):
    name = "dummy_alternating"

    def __init__(self) -> None:
        self._last_signal: Signal | None = None

    def decide(self, window: pd.DataFrame) -> Signal:
        if len(window) < 2:
            return Signal.HOLD
        last_close = float(window["close"].iloc[-1])
        prev_close = float(window["close"].iloc[-2])
        if last_close > prev_close:
            desired = Signal.ENTER_LONG
        elif last_close < prev_close:
            desired = Signal.ENTER_SHORT
        else:
            return Signal.HOLD

        if self._last_signal is not None and self._opposes(self._last_signal, desired):
            self._last_signal = Signal.EXIT
            return Signal.EXIT

        if self._last_signal == desired:
            return Signal.HOLD

        self._last_signal = desired
        return desired

    @staticmethod
    def _opposes(prev: Signal, desired: Signal) -> bool:
        return (prev, desired) in {
            (Signal.ENTER_LONG, Signal.ENTER_SHORT),
            (Signal.ENTER_SHORT, Signal.ENTER_LONG),
        }


__all__ = ["DummyAlternatingStrategy"]
