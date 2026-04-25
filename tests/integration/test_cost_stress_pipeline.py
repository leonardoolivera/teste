"""Integration: `cost_stress` end-to-end sobre MA 20/50 no sintético seminal (ADR-0014).

Pipeline de 4 perturbações + baseline = 5 linhas. Asserções estruturais:
tamanho da tabela, monotonicidade a cada passo (cenários ordenados por custo
crescente por construção), `max_drawdown ∈ [0, 1]` em todos.
"""

from __future__ import annotations

import pandas as pd
import pytest

from alpha_forge.backtest.cost import CostModel
from alpha_forge.data.loaders import DatasetNotFoundError, load_dataset
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.ma_crossover import (
    MovingAverageCrossoverStrategy,
)
from alpha_forge.validation import CostPerturbation, cost_stress

REFERENCE_DATASET_ID = "synthetic_btcusdt_1h_seed42"


@pytest.fixture(scope="module")
def prices() -> pd.DataFrame:
    try:
        return load_dataset(REFERENCE_DATASET_ID)
    except (DatasetNotFoundError, FileNotFoundError) as exc:
        pytest.skip(f"dataset seminal ausente: {exc}")


def test_cost_stress_pipeline(prices: pd.DataFrame) -> None:
    baseline = CostModel(taker_fee_bps=0.0, slippage_bps_per_unit_notional=0.0)
    perturbations = [
        CostPerturbation(label="fee+5", fee_delta_bps=5.0, slip_delta_bps=0.0),
        CostPerturbation(label="slip+5", fee_delta_bps=0.0, slip_delta_bps=5.0),
        CostPerturbation(label="both+10", fee_delta_bps=10.0, slip_delta_bps=10.0),
        CostPerturbation(label="both+50/100", fee_delta_bps=50.0, slip_delta_bps=100.0),
    ]

    report = cost_stress(
        prices=prices,
        strategy=MovingAverageCrossoverStrategy(short_window=20, long_window=50),
        budget=RiskBudget(
            capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0
        ),
        baseline_cost=baseline,
        perturbations=perturbations,
        dataset_id=REFERENCE_DATASET_ID,
    )

    assert report.dataset_id == REFERENCE_DATASET_ID
    assert len(report.scenarios) == 4
    assert [s.label for s in report.scenarios] == [
        "fee+5",
        "slip+5",
        "both+10",
        "both+50/100",
    ]

    # max_drawdown bem definido em todos os cenários (baseline + 4 perturbados)
    all_cells = [report.baseline, *report.scenarios]
    for cell in all_cells:
        assert cell.result.metrics is not None
        dd = cell.result.metrics.max_drawdown
        assert 0.0 <= dd <= 1.0

    # both+10 domina fee+5 (fee+=10 > fee+=5) → delta menor ou igual.
    # both+50/100 domina both+10 → delta menor ou igual.
    # (ADR-0010 por caminho explícito dentro do teste.)
    delta_fee5 = report.scenarios[0].final_equity_delta_vs_baseline
    delta_both10 = report.scenarios[2].final_equity_delta_vs_baseline
    delta_both_max = report.scenarios[3].final_equity_delta_vs_baseline
    tolerance = 1e-6 * 10_000.0
    assert delta_both10 <= delta_fee5 + tolerance
    assert delta_both_max <= delta_both10 + tolerance
