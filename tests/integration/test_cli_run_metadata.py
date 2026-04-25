"""Integration: CLI `validate` persiste `run.json` antes do pipeline (ADR-0017).

Garantias cobertas:
  - `run.json` existe após corrida bem-sucedida e carrega via `load_run_metadata`.
  - `run.json` sobrevive abort por ValidationError no meio do pipeline (rastro
    de auditoria mesmo em falha).
  - `flags` capturam todos os parâmetros argparse exceto `command`.
  - `timestamp_utc` é timezone-aware; monkeypatch de `_now_utc` produz round-trip
    bit-a-bit do instante injetado.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from alpha_forge.cli import app as cli_app
from alpha_forge.data.loaders import DatasetNotFoundError, load_dataset
from alpha_forge.validation import load_run_metadata

REFERENCE_DATASET_ID = "synthetic_btcusdt_1h_seed42"


@pytest.fixture(scope="module", autouse=True)
def _require_seminal_dataset() -> None:
    try:
        load_dataset(REFERENCE_DATASET_ID)
    except (DatasetNotFoundError, FileNotFoundError) as exc:
        pytest.skip(f"dataset seminal ausente: {exc}")


@pytest.fixture
def redirect_run_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    def _fake(run_id: str) -> Path:
        return tmp_path / "validation" / run_id

    monkeypatch.setattr(cli_app, "validation_run_dir", _fake)
    return _fake


FIXED_TS = datetime(2026, 4, 17, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def frozen_clock(monkeypatch: pytest.MonkeyPatch) -> datetime:
    monkeypatch.setattr(cli_app, "_now_utc", lambda: FIXED_TS)
    return FIXED_TS


class TestRunJsonEmCorridaOk:
    def test_run_json_existe_e_carrega(
        self, redirect_run_dir, frozen_clock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        run_id = "meta_test_ok"
        exit_code = cli_app.run(
            [
                "validate",
                "--run-id",
                run_id,
                "--dataset-id",
                REFERENCE_DATASET_ID,
                "--n-folds",
                "3",
                "--mc-resamples",
                "200",
            ]
        )
        assert exit_code == 0

        directory = redirect_run_dir(run_id)
        assert (directory / "run.json").exists()

        meta = load_run_metadata(directory=directory)
        assert meta.command == "validate"
        assert meta.run_id == run_id
        assert meta.timestamp_utc == frozen_clock
        assert meta.alpha_forge_version  # não vazio

        # flags contém os parâmetros passados e defaults; não contém `command`
        assert "command" not in meta.flags
        assert meta.flags["run_id"] == run_id
        assert meta.flags["dataset_id"] == REFERENCE_DATASET_ID
        assert meta.flags["n_folds"] == "3"
        assert meta.flags["mc_resamples"] == "200"
        assert meta.flags["skip_monte_carlo"] == "False"

        captured = capsys.readouterr()
        assert "run_metadata" in captured.out
        assert "run.json" in captured.out


class TestRunJsonSobreviveAbort:
    def test_run_json_persiste_mesmo_em_validation_error(
        self, redirect_run_dir, frozen_clock
    ) -> None:
        run_id = "meta_test_abort"
        # n_folds=1 < 2 → walk_forward levanta ValidationError.
        exit_code = cli_app.run(
            [
                "validate",
                "--run-id",
                run_id,
                "--dataset-id",
                REFERENCE_DATASET_ID,
                "--n-folds",
                "1",
            ]
        )
        assert exit_code == 1

        directory = redirect_run_dir(run_id)
        assert (directory / "run.json").exists()
        # Artefatos do pipeline não foram gravados porque abortou.
        assert not (directory / "walk_forward.json").exists()
        assert not (directory / "monte_carlo.json").exists()

        meta = load_run_metadata(directory=directory)
        assert meta.run_id == run_id
        assert meta.flags["n_folds"] == "1"


class TestFlagsCapturadas:
    def test_stress_repetido_serializa_como_lista(
        self, redirect_run_dir, frozen_clock
    ) -> None:
        run_id = "meta_test_stress"
        exit_code = cli_app.run(
            [
                "validate",
                "--run-id",
                run_id,
                "--dataset-id",
                REFERENCE_DATASET_ID,
                "--n-folds",
                "3",
                "--stress",
                "fee+10:10:0",
                "--stress",
                "slip+5:0:5",
            ]
        )
        assert exit_code == 0

        directory = redirect_run_dir(run_id)
        meta = load_run_metadata(directory=directory)
        # repr preserva as três partes e a ordem.
        assert "fee+10:10:0" in meta.flags["stress"]
        assert "slip+5:0:5" in meta.flags["stress"]

    def test_skip_flags_sao_persistidas(
        self, redirect_run_dir, frozen_clock
    ) -> None:
        run_id = "meta_test_skip"
        exit_code = cli_app.run(
            [
                "validate",
                "--run-id",
                run_id,
                "--dataset-id",
                REFERENCE_DATASET_ID,
                "--n-folds",
                "3",
                "--skip-monte-carlo",
                "--skip-cost-stress",
            ]
        )
        assert exit_code == 0

        directory = redirect_run_dir(run_id)
        meta = load_run_metadata(directory=directory)
        assert meta.flags["skip_monte_carlo"] == "True"
        assert meta.flags["skip_cost_stress"] == "True"

    def test_regime_filter_default_none(
        self, redirect_run_dir, frozen_clock
    ) -> None:
        run_id = "meta_test_regime_default"
        exit_code = cli_app.run(
            [
                "validate",
                "--run-id",
                run_id,
                "--dataset-id",
                REFERENCE_DATASET_ID,
                "--n-folds",
                "3",
                "--skip-monte-carlo",
            ]
        )
        assert exit_code == 0

        directory = redirect_run_dir(run_id)
        meta = load_run_metadata(directory=directory)
        # Default persiste como "none" via canonical_string (ADR-0022).
        assert meta.flags["regime_filter"] == "none"

    def test_regime_filter_sma_slope_canonicaliza(
        self, redirect_run_dir, frozen_clock
    ) -> None:
        run_id = "meta_test_regime_sma"
        exit_code = cli_app.run(
            [
                "validate",
                "--run-id",
                run_id,
                "--dataset-id",
                REFERENCE_DATASET_ID,
                "--n-folds",
                "3",
                "--skip-monte-carlo",
                "--regime-filter",
                "sma_slope:window=50:min_slope_bps=10",
            ]
        )
        assert exit_code == 0

        directory = redirect_run_dir(run_id)
        meta = load_run_metadata(directory=directory)
        # canonical_string ordena alfabeticamente: min_slope_bps antes de window.
        assert (
            meta.flags["regime_filter"]
            == "sma_slope:min_slope_bps=10:window=50"
        )

    def test_regime_filter_spec_invalido_rejeita(
        self, redirect_run_dir, frozen_clock
    ) -> None:
        with pytest.raises(SystemExit):
            cli_app.run(
                [
                    "validate",
                    "--run-id",
                    "meta_test_regime_bad",
                    "--dataset-id",
                    REFERENCE_DATASET_ID,
                    "--n-folds",
                    "3",
                    "--skip-monte-carlo",
                    "--regime-filter",
                    "nonexistent_filter:foo=1",
                ]
            )

    def test_regime_filter_atr_regime_canonicaliza(
        self, redirect_run_dir, frozen_clock
    ) -> None:
        run_id = "meta_test_regime_atr"
        exit_code = cli_app.run(
            [
                "validate",
                "--run-id",
                run_id,
                "--dataset-id",
                REFERENCE_DATASET_ID,
                "--n-folds",
                "3",
                "--skip-monte-carlo",
                "--regime-filter",
                "atr_regime:window=14:min_atr_bps=50",
            ]
        )
        assert exit_code == 0

        directory = redirect_run_dir(run_id)
        meta = load_run_metadata(directory=directory)
        # canonical_string ordena alfabeticamente: min_atr_bps antes de window.
        assert (
            meta.flags["regime_filter"]
            == "atr_regime:min_atr_bps=50:window=14"
        )

    def test_regime_filter_composite_and_canonicaliza(
        self, redirect_run_dir, frozen_clock
    ) -> None:
        run_id = "meta_test_regime_composite"
        # Input com filtros em ordem "SMA,ATR"; canonical deve reordenar alfabeticamente.
        exit_code = cli_app.run(
            [
                "validate",
                "--run-id",
                run_id,
                "--dataset-id",
                REFERENCE_DATASET_ID,
                "--n-folds",
                "3",
                "--skip-monte-carlo",
                "--regime-filter",
                "and(sma_slope:window=50:min_slope_bps=10,atr_regime:window=14:min_atr_bps=50)",
            ]
        )
        assert exit_code == 0

        directory = redirect_run_dir(run_id)
        meta = load_run_metadata(directory=directory)
        # ADR-0023 canonical: filtros internos reordenados lexicograficamente — atr antes de sma.
        assert (
            meta.flags["regime_filter"]
            == "and(atr_regime:min_atr_bps=50:window=14,sma_slope:min_slope_bps=10:window=50)"
        )
