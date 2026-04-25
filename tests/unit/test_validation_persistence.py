"""Unit de `validation/persistence.py` (ADR-0015).

Três classes, uma por artefato. Round-trip bit-a-bit + incompatibilidade de
`schema_version` + JSON malformado + arquivo inexistente + criação do
diretório + inspeção direta do envelope gravado.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.schemas import (
    BacktestMetrics,
    BacktestResult,
    Side,
    Trade,
)
from alpha_forge.validation import (
    CostPerturbation,
    CostStressCell,
    CostStressReport,
    MonteCarloSummary,
    ValidationError,
    WalkForwardFold,
    WalkForwardWindow,
    load_cost_stress_report,
    load_monte_carlo_summary,
    load_walk_forward_folds,
    save_cost_stress_report,
    save_monte_carlo_summary,
    save_walk_forward_folds,
)


def _utc(y: int, m: int, d: int, h: int = 0) -> datetime:
    return datetime(y, m, d, h, tzinfo=timezone.utc)


def _sample_result(dataset_id: str = "ds") -> BacktestResult:
    trade = Trade(
        side=Side.LONG,
        entry_timestamp=_utc(2025, 1, 1),
        exit_timestamp=_utc(2025, 1, 2),
        entry_price=100.0,
        exit_price=105.0,
        size=1.0,
        pnl=5.0,
    )
    return BacktestResult(
        dataset_id=dataset_id,
        bars=24,
        fills=[],
        rejections=[],
        trades=[trade],
        final_equity=10_005.0,
        max_equity=10_005.0,
        min_equity=10_000.0,
        equity_curve=[(_utc(2025, 1, 1), 10_000.0), (_utc(2025, 1, 2), 10_005.0)],
        metrics=BacktestMetrics(
            total_pnl=5.0, trade_count=1, hit_rate=1.0, max_drawdown=0.0
        ),
    )


def _sample_fold(fold_index: int = 1) -> WalkForwardFold:
    return WalkForwardFold(
        fold_index=fold_index,
        train_window=WalkForwardWindow(
            start=_utc(2025, 1, 1), end=_utc(2025, 1, 15), bars=360
        ),
        test_window=WalkForwardWindow(
            start=_utc(2025, 1, 16), end=_utc(2025, 1, 31), bars=384
        ),
        result=_sample_result(dataset_id=f"ds#fold{fold_index}"),
    )


def _sample_mc() -> MonteCarloSummary:
    return MonteCarloSummary(
        n_resamples=1000,
        seed=42,
        final_equity_percentiles={5: 9500.0, 25: 9800.0, 50: 10000.0, 75: 10200.0, 95: 10500.0},
        max_drawdown_percentiles={5: 0.01, 25: 0.02, 50: 0.05, 75: 0.08, 95: 0.12},
        original_final_equity=10_050.0,
        original_max_drawdown=0.04,
    )


def _sample_report() -> CostStressReport:
    baseline_cell = CostStressCell(
        scenario_index=0,
        label="baseline",
        cost=CostModel(taker_fee_bps=0.0, slippage_bps_per_unit_notional=0.0),
        result=_sample_result(),
        final_equity=10_005.0,
        final_equity_delta_vs_baseline=0.0,
    )
    stress_cell = CostStressCell(
        scenario_index=1,
        label="fee+5",
        cost=CostModel(taker_fee_bps=5.0, slippage_bps_per_unit_notional=0.0),
        result=_sample_result(dataset_id="ds#stress1"),
        final_equity=10_000.0,
        final_equity_delta_vs_baseline=-5.0,
    )
    return CostStressReport(
        dataset_id="ds",
        baseline=baseline_cell,
        scenarios=[stress_cell],
    )


class TestWalkForwardPersistence:
    def test_round_trip_bit_a_bit(self, tmp_path: Path) -> None:
        folds = [_sample_fold(1), _sample_fold(2)]
        save_walk_forward_folds(folds=folds, directory=tmp_path)
        loaded = load_walk_forward_folds(directory=tmp_path)
        assert loaded == folds

    def test_round_trip_lista_vazia(self, tmp_path: Path) -> None:
        save_walk_forward_folds(folds=[], directory=tmp_path)
        loaded = load_walk_forward_folds(directory=tmp_path)
        assert loaded == []

    def test_retorna_path_correto(self, tmp_path: Path) -> None:
        path = save_walk_forward_folds(folds=[_sample_fold()], directory=tmp_path)
        assert path == tmp_path / "walk_forward.json"

    def test_cria_diretorio_inexistente(self, tmp_path: Path) -> None:
        target = tmp_path / "novo" / "sub"
        assert not target.exists()
        save_walk_forward_folds(folds=[_sample_fold()], directory=target)
        assert target.exists()

    def test_envelope_tem_schema_version_um(self, tmp_path: Path) -> None:
        save_walk_forward_folds(folds=[_sample_fold()], directory=tmp_path)
        raw = json.loads((tmp_path / "walk_forward.json").read_text(encoding="utf-8"))
        assert raw["schema_version"] == "1"
        assert "payload" in raw

    def test_schema_version_incompativel_levanta(self, tmp_path: Path) -> None:
        save_walk_forward_folds(folds=[_sample_fold()], directory=tmp_path)
        path = tmp_path / "walk_forward.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["schema_version"] = "2"
        path.write_text(json.dumps(raw), encoding="utf-8")
        with pytest.raises(ValidationError, match="schema_version incompatível"):
            load_walk_forward_folds(directory=tmp_path)

    def test_json_malformado_levanta(self, tmp_path: Path) -> None:
        (tmp_path / "walk_forward.json").write_text("{not json", encoding="utf-8")
        with pytest.raises(ValidationError, match="JSON malformado"):
            load_walk_forward_folds(directory=tmp_path)

    def test_arquivo_inexistente_levanta_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_walk_forward_folds(directory=tmp_path)

    def test_sobrescrita_permitida(self, tmp_path: Path) -> None:
        save_walk_forward_folds(folds=[_sample_fold(1)], directory=tmp_path)
        save_walk_forward_folds(folds=[_sample_fold(2), _sample_fold(3)], directory=tmp_path)
        loaded = load_walk_forward_folds(directory=tmp_path)
        assert [f.fold_index for f in loaded] == [2, 3]


class TestMonteCarloPersistence:
    def test_round_trip_bit_a_bit(self, tmp_path: Path) -> None:
        summary = _sample_mc()
        save_monte_carlo_summary(summary=summary, directory=tmp_path)
        loaded = load_monte_carlo_summary(directory=tmp_path)
        assert loaded == summary

    def test_retorna_path_correto(self, tmp_path: Path) -> None:
        path = save_monte_carlo_summary(summary=_sample_mc(), directory=tmp_path)
        assert path == tmp_path / "monte_carlo.json"

    def test_envelope_tem_schema_version_um(self, tmp_path: Path) -> None:
        save_monte_carlo_summary(summary=_sample_mc(), directory=tmp_path)
        raw = json.loads((tmp_path / "monte_carlo.json").read_text(encoding="utf-8"))
        assert raw["schema_version"] == "1"

    def test_schema_version_incompativel_levanta(self, tmp_path: Path) -> None:
        save_monte_carlo_summary(summary=_sample_mc(), directory=tmp_path)
        path = tmp_path / "monte_carlo.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["schema_version"] = "99"
        path.write_text(json.dumps(raw), encoding="utf-8")
        with pytest.raises(ValidationError, match="schema_version incompatível"):
            load_monte_carlo_summary(directory=tmp_path)

    def test_envelope_sem_payload_levanta(self, tmp_path: Path) -> None:
        path = tmp_path / "monte_carlo.json"
        path.write_text(json.dumps({"schema_version": "1"}), encoding="utf-8")
        with pytest.raises(ValidationError, match="envelope inválido"):
            load_monte_carlo_summary(directory=tmp_path)

    def test_arquivo_inexistente_levanta_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_monte_carlo_summary(directory=tmp_path)


class TestCostStressPersistence:
    def test_round_trip_bit_a_bit(self, tmp_path: Path) -> None:
        report = _sample_report()
        save_cost_stress_report(report=report, directory=tmp_path)
        loaded = load_cost_stress_report(directory=tmp_path)
        assert loaded == report

    def test_retorna_path_correto(self, tmp_path: Path) -> None:
        path = save_cost_stress_report(report=_sample_report(), directory=tmp_path)
        assert path == tmp_path / "cost_stress.json"

    def test_envelope_tem_schema_version_um(self, tmp_path: Path) -> None:
        save_cost_stress_report(report=_sample_report(), directory=tmp_path)
        raw = json.loads((tmp_path / "cost_stress.json").read_text(encoding="utf-8"))
        assert raw["schema_version"] == "1"

    def test_schema_version_incompativel_levanta(self, tmp_path: Path) -> None:
        save_cost_stress_report(report=_sample_report(), directory=tmp_path)
        path = tmp_path / "cost_stress.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["schema_version"] = "0"
        path.write_text(json.dumps(raw), encoding="utf-8")
        with pytest.raises(ValidationError, match="schema_version incompatível"):
            load_cost_stress_report(directory=tmp_path)

    def test_payload_violando_schema_levanta(self, tmp_path: Path) -> None:
        save_cost_stress_report(report=_sample_report(), directory=tmp_path)
        path = tmp_path / "cost_stress.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["payload"]["scenarios"] = []  # viola min_length=1
        path.write_text(json.dumps(raw), encoding="utf-8")
        with pytest.raises(ValidationError, match="viola schema CostStressReport"):
            load_cost_stress_report(directory=tmp_path)

    def test_arquivo_inexistente_levanta_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_cost_stress_report(directory=tmp_path)

    def test_payload_antigo_sem_spread_bps_carrega_com_default_zero(
        self, tmp_path: Path
    ) -> None:
        # ADR-0019 §"Persistência": schema_version não muda; payloads gravados
        # antes do campo `spread_bps` carregam com default 0.0 via pydantic,
        # preservando retrocompat bit-a-bit dos artefatos históricos.
        save_cost_stress_report(report=_sample_report(), directory=tmp_path)
        path = tmp_path / "cost_stress.json"
        raw = json.loads(path.read_text(encoding="utf-8"))

        # Remove os campos novos de todas as CostModel e CostPerturbation
        # embutidas no payload, simulando um JSON gravado pré-E.9.
        def _strip(obj: object) -> None:
            if isinstance(obj, dict):
                obj.pop("spread_bps", None)
                obj.pop("spread_delta_bps", None)
                for value in obj.values():
                    _strip(value)
            elif isinstance(obj, list):
                for item in obj:
                    _strip(item)

        _strip(raw)
        path.write_text(json.dumps(raw), encoding="utf-8")

        loaded = load_cost_stress_report(directory=tmp_path)
        assert loaded.baseline.cost.spread_bps == 0.0
        for cell in loaded.scenarios:
            assert cell.cost.spread_bps == 0.0


class TestArtefatosIndependentes:
    """Cada artefato é opcional: salvar um não obriga salvar os outros."""

    def test_salvar_um_nao_cria_outros(self, tmp_path: Path) -> None:
        save_monte_carlo_summary(summary=_sample_mc(), directory=tmp_path)
        assert (tmp_path / "monte_carlo.json").exists()
        assert not (tmp_path / "walk_forward.json").exists()
        assert not (tmp_path / "cost_stress.json").exists()

    def test_carregar_artefato_ausente_levanta(self, tmp_path: Path) -> None:
        save_monte_carlo_summary(summary=_sample_mc(), directory=tmp_path)
        with pytest.raises(FileNotFoundError):
            load_walk_forward_folds(directory=tmp_path)
        with pytest.raises(FileNotFoundError):
            load_cost_stress_report(directory=tmp_path)
