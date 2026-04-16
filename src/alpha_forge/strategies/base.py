"""Contrato base de estratégia (ADR-0002, Contrato A — janela causal).

Estratégias recebem apenas a janela ``prices[:t+1]`` a cada passo e retornam
um `Signal`. Sem acesso ao dataset completo; sem estado oculto além do que
a própria estratégia decidir guardar.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from alpha_forge.backtest.schemas import Signal


class Strategy(ABC):
    """Interface mínima. Subclasses implementam `decide`."""

    name: str = "strategy"

    @abstractmethod
    def decide(self, window: pd.DataFrame) -> Signal:
        """Decisão causal sobre a janela até `t` (inclusive).

        `window` tem as colunas ``open, high, low, close, volume`` e
        `window.iloc[-1]` é a barra `t`. A execução acontecerá em `t+1 open`.
        """
