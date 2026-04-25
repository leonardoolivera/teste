"""Stress de custos sistematizado (ADR-0014).

Dado um cenário fixo (dataset + estratégia + budget + baseline `CostModel`) e
uma lista de perturbações aditivas em bps, roda `run_backtest` uma vez por
cenário (baseline + N perturbações) e devolve um `CostStressReport` com a
tabela resultante.

Monotonicidade ADR-0010 é assertada por cenário antes do retorno — violação
é bug, não flakiness.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

import pandas as pd

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import StrategyProtocol, run_backtest
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.validation.schemas import (
    CostPerturbation,
    CostStressCell,
    CostStressReport,
)
from alpha_forge.validation.walk_forward import ValidationError

if TYPE_CHECKING:
    from alpha_forge.regimes import RegimeFilter


def cost_stress(
    *,
    prices: pd.DataFrame,
    strategy: StrategyProtocol,
    budget: RiskBudget,
    baseline_cost: CostModel,
    perturbations: Sequence[CostPerturbation],
    dataset_id: str,
    regime_filter: "RegimeFilter | None" = None,
) -> CostStressReport:
    """Roda `N+1` backtests e devolve a tabela de stress (ADR-0014).

    Ordem: baseline primeiro (`scenario_index=0`), depois cada perturbação na
    ordem da lista (`scenario_index=k+1` para a k-ésima perturbação).

    Validações eager:
      - `perturbations` não-vazio.
      - Pelo menos uma perturbação estritamente positiva em algum componente.
      - Labels únicos dentro de `perturbations`.

    Asserção (defesa em profundidade sobre ADR-0010):
      - Para cada `scenario_index ≥ 1`,
        `final_equity_delta_vs_baseline <= 1e-6 * budget.capital_inicial`.
        Violação levanta `ValidationError` — o engine está em estado
        inconsistente e o relatório não pode ser confiável.
    """
    if not perturbations:
        raise ValidationError(
            "perturbations vazio — stress sem cenário é backtest único"
        )

    any_strict_positive = any(
        p.fee_delta_bps > 0.0
        or p.slip_delta_bps > 0.0
        or p.spread_delta_bps > 0.0
        for p in perturbations
    )
    if not any_strict_positive:
        raise ValidationError(
            "perturbations são todos zero — relatório seria degenerado "
            "(cópia do baseline)"
        )

    labels = [p.label for p in perturbations]
    if len(set(labels)) != len(labels):
        raise ValidationError(
            f"labels duplicados em perturbations: {labels!r}"
        )

    baseline_result = run_backtest(
        prices=prices,
        strategy=strategy,
        budget=budget,
        cost_model=baseline_cost,
        dataset_id=dataset_id,
        regime_filter=regime_filter,
    )
    baseline_cell = CostStressCell(
        scenario_index=0,
        label="baseline",
        cost=baseline_cost,
        result=baseline_result,
        final_equity=baseline_result.final_equity,
        final_equity_delta_vs_baseline=0.0,
    )

    tolerance = 1e-6 * budget.capital_inicial
    scenarios: list[CostStressCell] = []
    for k, pert in enumerate(perturbations, start=1):
        effective_cost = CostModel(
            taker_fee_bps=baseline_cost.taker_fee_bps + pert.fee_delta_bps,
            slippage_bps_per_unit_notional=(
                baseline_cost.slippage_bps_per_unit_notional + pert.slip_delta_bps
            ),
            spread_bps=baseline_cost.spread_bps + pert.spread_delta_bps,
        )
        scenario_result = run_backtest(
            prices=prices,
            strategy=strategy,
            budget=budget,
            cost_model=effective_cost,
            dataset_id=f"{dataset_id}#stress{k}",
            regime_filter=regime_filter,
        )
        delta = scenario_result.final_equity - baseline_result.final_equity
        if delta > tolerance:
            raise ValidationError(
                f"ADR-0010 violada em scenario_index={k} (label={pert.label!r}): "
                f"final_equity subiu com custo maior "
                f"(delta={delta:.10f}, tolerance={tolerance:.10f}). "
                f"Isto é bug de engine, não flakiness."
            )
        scenarios.append(
            CostStressCell(
                scenario_index=k,
                label=pert.label,
                cost=effective_cost,
                result=scenario_result,
                final_equity=scenario_result.final_equity,
                final_equity_delta_vs_baseline=delta,
            )
        )

    return CostStressReport(
        dataset_id=dataset_id,
        baseline=baseline_cell,
        scenarios=scenarios,
    )
