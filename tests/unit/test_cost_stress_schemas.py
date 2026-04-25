"""Validação estrutural dos schemas de stress de custos (ADR-0014).

Mesmo padrão do `test_validation_schemas.py`: frozen + extra=forbid; validators
numéricos rejeitam valores inválidos na construção.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError as PydanticValidationError

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.schemas import BacktestResult
from alpha_forge.validation.schemas import (
    CostPerturbation,
    CostStressCell,
    CostStressReport,
)


def _utc(y: int, m: int, d: int) -> datetime:
    return datetime(y, m, d, tzinfo=timezone.utc)


def _empty_result(dataset_id: str = "ds") -> BacktestResult:
    return BacktestResult(
        dataset_id=dataset_id,
        bars=0,
        fills=[],
        rejections=[],
        trades=[],
        final_equity=10_000.0,
        max_equity=10_000.0,
        min_equity=10_000.0,
        equity_curve=[(_utc(2025, 1, 1), 10_000.0)],
        metrics=None,
    )


class TestCostPerturbation:
    def test_constroi_com_campos_validos(self) -> None:
        p = CostPerturbation(label="fee+5", fee_delta_bps=5.0, slip_delta_bps=0.0)
        assert p.label == "fee+5"
        assert p.fee_delta_bps == 5.0

    def test_rejeita_fee_negativo(self) -> None:
        with pytest.raises(PydanticValidationError):
            CostPerturbation(label="x", fee_delta_bps=-0.1, slip_delta_bps=0.0)

    def test_rejeita_slip_negativo(self) -> None:
        with pytest.raises(PydanticValidationError):
            CostPerturbation(label="x", fee_delta_bps=0.0, slip_delta_bps=-0.1)

    def test_rejeita_label_vazio(self) -> None:
        with pytest.raises(PydanticValidationError):
            CostPerturbation(label="", fee_delta_bps=1.0, slip_delta_bps=0.0)

    def test_frozen(self) -> None:
        p = CostPerturbation(label="x", fee_delta_bps=1.0, slip_delta_bps=0.0)
        with pytest.raises(PydanticValidationError):
            p.fee_delta_bps = 99.0  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        with pytest.raises(PydanticValidationError):
            CostPerturbation(
                label="x",
                fee_delta_bps=1.0,
                slip_delta_bps=0.0,
                extra=1,  # type: ignore[call-arg]
            )

    def test_spread_delta_default_zero(self) -> None:
        # ADR-0019: campo opcional com default zero preserva construtores antigos.
        p = CostPerturbation(label="x", fee_delta_bps=1.0, slip_delta_bps=0.0)
        assert p.spread_delta_bps == 0.0

    def test_spread_delta_rejeita_negativo(self) -> None:
        with pytest.raises(PydanticValidationError):
            CostPerturbation(
                label="x",
                fee_delta_bps=0.0,
                slip_delta_bps=0.0,
                spread_delta_bps=-0.1,
            )

    def test_spread_delta_positivo_aceito(self) -> None:
        p = CostPerturbation(
            label="x", fee_delta_bps=0.0, slip_delta_bps=0.0, spread_delta_bps=5.0
        )
        assert p.spread_delta_bps == 5.0


class TestCostStressCell:
    def _base_kwargs(self) -> dict[str, object]:
        return {
            "scenario_index": 1,
            "label": "fee+5",
            "cost": CostModel(taker_fee_bps=5.0, slippage_bps_per_unit_notional=2.0),
            "result": _empty_result(),
            "final_equity": 9_995.0,
            "final_equity_delta_vs_baseline": -5.0,
        }

    def test_constroi_com_campos_validos(self) -> None:
        c = CostStressCell(**self._base_kwargs())  # type: ignore[arg-type]
        assert c.scenario_index == 1

    def test_rejeita_scenario_index_negativo(self) -> None:
        kwargs = self._base_kwargs()
        kwargs["scenario_index"] = -1
        with pytest.raises(PydanticValidationError):
            CostStressCell(**kwargs)  # type: ignore[arg-type]

    def test_rejeita_label_vazio(self) -> None:
        kwargs = self._base_kwargs()
        kwargs["label"] = ""
        with pytest.raises(PydanticValidationError):
            CostStressCell(**kwargs)  # type: ignore[arg-type]

    def test_frozen(self) -> None:
        c = CostStressCell(**self._base_kwargs())  # type: ignore[arg-type]
        with pytest.raises(PydanticValidationError):
            c.scenario_index = 99  # type: ignore[misc]


class TestCostStressReport:
    def _cell(self, idx: int, label: str) -> CostStressCell:
        return CostStressCell(
            scenario_index=idx,
            label=label,
            cost=CostModel(taker_fee_bps=0.0, slippage_bps_per_unit_notional=0.0),
            result=_empty_result(),
            final_equity=10_000.0,
            final_equity_delta_vs_baseline=0.0,
        )

    def test_constroi_com_um_cenario(self) -> None:
        r = CostStressReport(
            dataset_id="ds",
            baseline=self._cell(0, "baseline"),
            scenarios=[self._cell(1, "fee+5")],
        )
        assert len(r.scenarios) == 1

    def test_rejeita_scenarios_vazio(self) -> None:
        with pytest.raises(PydanticValidationError):
            CostStressReport(
                dataset_id="ds",
                baseline=self._cell(0, "baseline"),
                scenarios=[],
            )

    def test_rejeita_dataset_id_vazio(self) -> None:
        with pytest.raises(PydanticValidationError):
            CostStressReport(
                dataset_id="",
                baseline=self._cell(0, "baseline"),
                scenarios=[self._cell(1, "x")],
            )

    def test_frozen(self) -> None:
        r = CostStressReport(
            dataset_id="ds",
            baseline=self._cell(0, "baseline"),
            scenarios=[self._cell(1, "x")],
        )
        with pytest.raises(PydanticValidationError):
            r.dataset_id = "y"  # type: ignore[misc]
