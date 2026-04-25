"""Contratos do módulo `risk` (ADR-0004, ADR-0063, ADR-0180).

Núcleo mínimo: apenas `RiskBudget`. Sem sizing adaptativo, sem equity guard,
sem agregados. Limite de alavancagem é hard cap.

ADR-0063 adiciona `SizingMode`: default `FIXED_NOTIONAL` preserva comportamento
bit-a-bit. `SNOWBALL` usa capital_corrente = capital_inicial + realized_pnl.

ADR-0180 adiciona `PYRAMID_EQUITY`: stack de até N tranches, cada uma dimensionada
como fração do equity mark-to-market corrente. Pyramid mode requer os 3 params
opcionais preenchidos; valida em model_validator.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SizingMode(str, Enum):
    """Modo de sizing (ADR-0063, ADR-0180).

    - ``FIXED_NOTIONAL``: capital_corrente sempre = capital_inicial.
    - ``SNOWBALL``: capital_corrente = capital_inicial + sum(realized pnl).
    - ``PYRAMID_EQUITY``: stack de tranches; cada tranche k dimensionada
      como ``tranche_equity_fraction × equity_mark_to_market × alavancagem``.
      Requer ``pyramid_max_tranches`` + ``pyramid_tranche_equity_fraction``
      + ``pyramid_rearm_cooldown_bars`` em ``RiskBudget`` (ADR-0180 §execution_hints).
    """

    FIXED_NOTIONAL = "fixed_notional"
    SNOWBALL = "snowball"
    PYRAMID_EQUITY = "pyramid_equity"


class RiskBudget(BaseModel):
    """Governança mínima de risco para uma execução.

    - ``capital_inicial``: capital disponível em unidades de conta (ex.: USDT).
    - ``fracao_por_trade``: fração do capital arriscada por trade, ∈ (0, 1].
      Ignorado quando ``sizing_mode == PYRAMID_EQUITY`` (pyramid usa
      ``pyramid_tranche_equity_fraction``).
    - ``alavancagem_max``: hard cap entre 1 e 10 (ADR-0004 e vision/01-product.md).
    - ``sizing_mode``: ADR-0063/0180; default FIXED_NOTIONAL preserva contrato v1.
    - ``pyramid_max_tranches``: ADR-0180; int ∈ [1, 10]. Obrigatório em PYRAMID_EQUITY.
    - ``pyramid_tranche_equity_fraction``: ADR-0180; float ∈ (0, 1]. Obrigatório em PYRAMID_EQUITY.
    - ``pyramid_rearm_cooldown_bars``: ADR-0180; int ≥ 0. Obrigatório em PYRAMID_EQUITY.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    capital_inicial: float = Field(gt=0.0)
    fracao_por_trade: float = Field(gt=0.0, le=1.0)
    alavancagem_max: float = Field(ge=1.0, le=10.0)
    sizing_mode: SizingMode = SizingMode.FIXED_NOTIONAL
    pyramid_max_tranches: Optional[int] = Field(default=None, ge=1, le=10)
    pyramid_tranche_equity_fraction: Optional[float] = Field(default=None, gt=0.0, le=1.0)
    pyramid_rearm_cooldown_bars: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _validate_pyramid_consistency(self) -> "RiskBudget":
        pyr_fields = (
            self.pyramid_max_tranches,
            self.pyramid_tranche_equity_fraction,
            self.pyramid_rearm_cooldown_bars,
        )
        if self.sizing_mode == SizingMode.PYRAMID_EQUITY:
            if any(f is None for f in pyr_fields):
                raise ValueError(
                    "PYRAMID_EQUITY exige pyramid_max_tranches, "
                    "pyramid_tranche_equity_fraction e pyramid_rearm_cooldown_bars "
                    "(ADR-0180 §execution_hints)."
                )
        else:
            if any(f is not None for f in pyr_fields):
                raise ValueError(
                    "pyramid_* só são aceitos quando sizing_mode=PYRAMID_EQUITY "
                    "(ADR-0180)."
                )
        return self
