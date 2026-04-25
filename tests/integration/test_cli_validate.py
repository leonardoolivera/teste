"""Integration: subcomando `alpha-forge validate` end-to-end (ADR-0016).

Roda `run(["validate", ...])` com `--run-id` redirecionado para `tmp_path` via
monkeypatch de `validation_run_dir` dentro de `cli.app`. Confirma que os três
artefatos são gravados, carregáveis, e que as flags de skip funcionam.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alpha_forge.cli import app as cli_app
from alpha_forge.data.loaders import DatasetNotFoundError, load_dataset
from alpha_forge.validation import (
    load_cost_stress_report,
    load_monte_carlo_summary,
    load_walk_forward_folds,
)

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


class TestValidatePipelineCompleto:
    def test_walk_forward_mc_e_stress_persistem_e_sao_carregaveis(
        self, redirect_run_dir, capsys: pytest.CaptureFixture[str]
    ) -> None:
        run_id = "cli_test_full"
        exit_code = cli_app.run(
            [
                "validate",
                "--run-id",
                run_id,
                "--dataset-id",
                REFERENCE_DATASET_ID,
                "--n-folds",
                "5",
                "--mc-resamples",
                "500",
                "--mc-seed",
                "42",
                "--stress",
                "fee+10:10:0",
                "--stress",
                "slip+10:0:10",
            ]
        )
        assert exit_code == 0

        directory = redirect_run_dir(run_id)
        folds = load_walk_forward_folds(directory=directory)
        mc = load_monte_carlo_summary(directory=directory)
        stress = load_cost_stress_report(directory=directory)

        assert len(folds) >= 1
        assert mc.n_resamples == 500
        assert mc.seed == 42
        assert [s.label for s in stress.scenarios] == ["fee+10", "slip+10"]

        captured = capsys.readouterr()
        assert "walk_forward" in captured.out
        assert "monte_carlo" in captured.out
        assert "cost_stress" in captured.out
        assert run_id in captured.out


class TestValidateSkipFlags:
    def test_skip_monte_carlo_nao_grava_mc(
        self, redirect_run_dir, capsys: pytest.CaptureFixture[str]
    ) -> None:
        run_id = "cli_test_skip_mc"
        exit_code = cli_app.run(
            [
                "validate",
                "--run-id",
                run_id,
                "--dataset-id",
                REFERENCE_DATASET_ID,
                "--skip-monte-carlo",
                "--stress",
                "fee+10:10:0",
            ]
        )
        assert exit_code == 0

        directory = redirect_run_dir(run_id)
        assert (directory / "walk_forward.json").exists()
        assert not (directory / "monte_carlo.json").exists()
        assert (directory / "cost_stress.json").exists()

        captured = capsys.readouterr()
        assert "monte_carlo      : pulado" in captured.out

    def test_skip_cost_stress_nao_grava_stress(
        self, redirect_run_dir, capsys: pytest.CaptureFixture[str]
    ) -> None:
        run_id = "cli_test_skip_stress"
        exit_code = cli_app.run(
            [
                "validate",
                "--run-id",
                run_id,
                "--dataset-id",
                REFERENCE_DATASET_ID,
                "--skip-cost-stress",
            ]
        )
        assert exit_code == 0

        directory = redirect_run_dir(run_id)
        assert (directory / "walk_forward.json").exists()
        assert (directory / "monte_carlo.json").exists()
        assert not (directory / "cost_stress.json").exists()

    def test_sem_stress_e_sem_skip_pula_cost_stress(
        self, redirect_run_dir, capsys: pytest.CaptureFixture[str]
    ) -> None:
        run_id = "cli_test_no_stress"
        exit_code = cli_app.run(
            [
                "validate",
                "--run-id",
                run_id,
                "--dataset-id",
                REFERENCE_DATASET_ID,
            ]
        )
        assert exit_code == 0

        directory = redirect_run_dir(run_id)
        assert (directory / "walk_forward.json").exists()
        assert (directory / "monte_carlo.json").exists()
        assert not (directory / "cost_stress.json").exists()

        captured = capsys.readouterr()
        assert "sem --stress" in captured.out


class TestValidateErros:
    def test_stress_malformado_erro_de_cli(
        self, redirect_run_dir, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # argparse `error()` chama sys.exit(2) — capturamos via SystemExit.
        with pytest.raises(SystemExit) as exc:
            cli_app.run(
                [
                    "validate",
                    "--run-id",
                    "x",
                    "--dataset-id",
                    REFERENCE_DATASET_ID,
                    "--stress",
                    "malformado",
                ]
            )
        assert exc.value.code == 2

    def test_validation_error_sai_com_codigo_1(
        self, redirect_run_dir, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # n_folds=1 < 2 dispara ValidationError dentro de walk_forward.
        exit_code = cli_app.run(
            [
                "validate",
                "--run-id",
                "cli_test_error",
                "--dataset-id",
                REFERENCE_DATASET_ID,
                "--n-folds",
                "1",
            ]
        )
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "erro:" in captured.err
