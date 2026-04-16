"""Contratos do módulo `risk` (ADR-0004).

Núcleo mínimo: apenas `RiskBudget`. Sem sizing adaptativo, sem equity guard,
sem agregados. Limite de alavancagem é hard cap.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RiskBudget(BaseModel):
    """Governança mínima de risco para uma execução.

    - ``capital_inicial``: capital disponível em unidades de conta (ex.: USDT).
    - ``fracao_por_trade``: fração do capital arriscada por trade, ∈ (0, 1].
    - ``alavancagem_max``: hard cap entre 1 e 10 (ADR-0004 e vision/01-product.md).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    capital_inicial: float = Field(gt=0.0)
    fracao_por_trade: float = Field(gt=0.0, le=1.0)
    alavancagem_max: float = Field(ge=1.0, le=10.0)
