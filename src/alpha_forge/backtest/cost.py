"""Modelo mínimo de custos de execução (ADR-0006 + ADR-0019).

Três componentes, aplicados diretamente no preço de execução:
  - `taker_fee_bps` — fee base em basis points, cobrada em toda entrada e saída.
  - `slippage_bps_per_unit_notional` — bps de slippage por unidade de
    ``notional / capital_inicial`` (linear).
  - `spread_bps` — half-spread efetivo em basis points, estrutural e
    independente de notional (ADR-0019).

Nenhum maker, funding ou modelo dependente de ativo.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from alpha_forge.backtest.schemas import Side


class CostModel(BaseModel):
    """Contrato de custos declarado por execução de backtest."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    taker_fee_bps: float = Field(ge=0.0)
    slippage_bps_per_unit_notional: float = Field(ge=0.0)
    spread_bps: float = Field(ge=0.0, default=0.0)


def zero_cost() -> CostModel:
    """Helper que deixa ``cost_model=zero_cost()`` explícito em testes e scripts.

    Uso deliberado: a API não tem default zero. Se o chamador quer custo
    zero, constrói aqui — fica claro no código que era intencional.
    """
    return CostModel(taker_fee_bps=0.0, slippage_bps_per_unit_notional=0.0)


def apply_cost(
    *,
    price_market: float,
    notional: float,
    capital_inicial: float,
    side: Side,
    is_entry: bool,
    cost_model: CostModel,
) -> float:
    """Retorna o preço efetivo após aplicar fee + slippage.

    O ajuste é sempre **contra o trader**:
      - compra (entrada long ou saída short) → preço sobe.
      - venda (saída long ou entrada short) → preço cai.

    Função pura. Não verifica `price_market > 0` nem `capital_inicial > 0`;
    essas invariantes vivem no engine (rejeição determinística) e no
    `RiskBudget` (validação pydantic).
    """
    if capital_inicial <= 0.0:
        return price_market

    exposure_ratio = notional / capital_inicial
    total_bps = (
        cost_model.taker_fee_bps
        + cost_model.slippage_bps_per_unit_notional * exposure_ratio
        + cost_model.spread_bps
    )
    factor = total_bps / 10_000.0

    buying = (is_entry and side == Side.LONG) or (not is_entry and side == Side.SHORT)

    if buying:
        return price_market * (1.0 + factor)
    return price_market * (1.0 - factor)
