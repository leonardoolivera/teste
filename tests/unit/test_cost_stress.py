"""Unit de `cost_stress` (ADR-0014).

Cobre: validações eager (vazio, todo zero, labels duplicados), shape feliz
(baseline em scenario_index=0, perturbações na ordem da lista, aritmética do
aditivo bit-a-bit, sufixo `#stress{k}` no `dataset_id`), monotonicidade
asseverada (pelo `cost_stress` em si — se falhar, é bug do engine).
"""

from __future__ import annotations

import pandas as pd
import pytest

from alpha_forge.backtest.cost import CostModel, zero_cost
from alpha_forge.data.loaders import DatasetNotFoundError, load_dataset
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.ma_crossover import (
    MovingAverageCrossoverStrategy,
)
from alpha_forge.validation import (
    CostPerturbation,
    ValidationError,
    cost_stress,
)

REFERENCE_DATASET_ID = "synthetic_btcusdt_1h_seed42"


@pytest.fixture(scope="module")
def prices() -> pd.DataFrame:
    try:
        return load_dataset(REFERENCE_DATASET_ID)
    except (DatasetNotFoundError, FileNotFoundError) as exc:
        pytest.skip(f"dataset seminal ausente: {exc}")


def _strategy() -> MovingAverageCrossoverStrategy:
    return MovingAverageCrossoverStrategy(short_window=20, long_window=50)


def _budget() -> RiskBudget:
    return RiskBudget(
        capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0
    )


class TestValidacoesEager:
    def test_perturbations_vazio_levanta(self, prices: pd.DataFrame) -> None:
        with pytest.raises(ValidationError, match="vazio"):
            cost_stress(
                prices=prices,
                strategy=_strategy(),
                budget=_budget(),
                baseline_cost=zero_cost(),
                perturbations=[],
                dataset_id=REFERENCE_DATASET_ID,
            )

    def test_perturbations_todo_zero_levanta(self, prices: pd.DataFrame) -> None:
        with pytest.raises(ValidationError, match="todos zero"):
            cost_stress(
                prices=prices,
                strategy=_strategy(),
                budget=_budget(),
                baseline_cost=zero_cost(),
                perturbations=[
                    CostPerturbation(
                        label="zero", fee_delta_bps=0.0, slip_delta_bps=0.0
                    )
                ],
                dataset_id=REFERENCE_DATASET_ID,
            )

    def test_apenas_spread_delta_positivo_e_aceito(
        self, prices: pd.DataFrame
    ) -> None:
        # ADR-0019: spread_delta_bps > 0 com fee=0 e slip=0 é stress válido
        # (antes de E.9, essa combinação seria rejeitada como "todos zero").
        report = cost_stress(
            prices=prices,
            strategy=_strategy(),
            budget=_budget(),
            baseline_cost=zero_cost(),
            perturbations=[
                CostPerturbation(
                    label="spread+5",
                    fee_delta_bps=0.0,
                    slip_delta_bps=0.0,
                    spread_delta_bps=5.0,
                )
            ],
            dataset_id=REFERENCE_DATASET_ID,
        )
        assert report.scenarios[0].cost.spread_bps == 5.0

    def test_labels_duplicados_levanta(self, prices: pd.DataFrame) -> None:
        with pytest.raises(ValidationError, match="duplicados"):
            cost_stress(
                prices=prices,
                strategy=_strategy(),
                budget=_budget(),
                baseline_cost=zero_cost(),
                perturbations=[
                    CostPerturbation(
                        label="mesmo", fee_delta_bps=5.0, slip_delta_bps=0.0
                    ),
                    CostPerturbation(
                        label="mesmo", fee_delta_bps=10.0, slip_delta_bps=0.0
                    ),
                ],
                dataset_id=REFERENCE_DATASET_ID,
            )


class TestChamadaFeliz:
    def _report(self, prices: pd.DataFrame):
        return cost_stress(
            prices=prices,
            strategy=_strategy(),
            budget=_budget(),
            baseline_cost=CostModel(
                taker_fee_bps=1.0, slippage_bps_per_unit_notional=0.5
            ),
            perturbations=[
                CostPerturbation(label="fee+5", fee_delta_bps=5.0, slip_delta_bps=0.0),
                CostPerturbation(label="slip+5", fee_delta_bps=0.0, slip_delta_bps=5.0),
            ],
            dataset_id=REFERENCE_DATASET_ID,
        )

    def test_baseline_scenario_index_zero(self, prices: pd.DataFrame) -> None:
        r = self._report(prices)
        assert r.baseline.scenario_index == 0
        assert r.baseline.label == "baseline"
        assert r.baseline.final_equity_delta_vs_baseline == 0.0

    def test_scenarios_indices_crescentes_a_partir_de_um(
        self, prices: pd.DataFrame
    ) -> None:
        r = self._report(prices)
        assert [s.scenario_index for s in r.scenarios] == [1, 2]

    def test_labels_propagados_na_ordem(self, prices: pd.DataFrame) -> None:
        r = self._report(prices)
        assert [s.label for s in r.scenarios] == ["fee+5", "slip+5"]

    def test_aritmetica_aditiva_bit_a_bit(self, prices: pd.DataFrame) -> None:
        r = self._report(prices)
        # baseline = (1.0, 0.5); fee+5 = (6.0, 0.5); slip+5 = (1.0, 5.5)
        assert r.scenarios[0].cost.taker_fee_bps == 6.0
        assert r.scenarios[0].cost.slippage_bps_per_unit_notional == 0.5
        assert r.scenarios[1].cost.taker_fee_bps == 1.0
        assert r.scenarios[1].cost.slippage_bps_per_unit_notional == 5.5

    def test_dataset_id_propagado_com_sufixo_stress(
        self, prices: pd.DataFrame
    ) -> None:
        r = self._report(prices)
        assert r.dataset_id == REFERENCE_DATASET_ID
        assert r.baseline.result.dataset_id == REFERENCE_DATASET_ID
        assert r.scenarios[0].result.dataset_id == f"{REFERENCE_DATASET_ID}#stress1"
        assert r.scenarios[1].result.dataset_id == f"{REFERENCE_DATASET_ID}#stress2"

    def test_monotonicidade_assertada_por_cenario(
        self, prices: pd.DataFrame
    ) -> None:
        """ADR-0010 reforçada: delta ≤ tolerância em todo scenario_index ≥ 1."""
        r = self._report(prices)
        tolerance = 1e-6 * _budget().capital_inicial
        for s in r.scenarios:
            assert s.final_equity_delta_vs_baseline <= tolerance
            # delta também deve ser = final_equity - baseline (consistência interna)
            assert s.final_equity_delta_vs_baseline == pytest.approx(
                s.final_equity - r.baseline.final_equity, abs=1e-9
            )
