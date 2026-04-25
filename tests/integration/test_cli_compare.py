"""Integration: subcomando `alpha-forge compare` end-to-end (ADR-0018).

Grava duas corridas sintéticas via `cli_app.run(["validate", ...])` em
`tmp_path` (usando o mesmo redirecionamento de `validation_run_dir` que os
testes de `validate`), depois chama `cli_app.run(["compare", ...])` e valida
saída/exit-code. Confirma que `compare` é read-only: não toca nos artefatos
originais e é idempotente sob re-execução.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alpha_forge.cli import app as cli_app
from alpha_forge.data.loaders import DatasetNotFoundError, load_dataset

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


def _run_validate(run_id: str, *extra: str) -> None:
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
            "--mc-seed",
            "42",
            "--stress",
            "fee+10:10:0",
            *extra,
        ]
    )
    assert exit_code == 0


class TestCompareCorridasReais:
    def test_duas_corridas_identicas_seed_fixo_seções_todas_presentes(
        self, redirect_run_dir, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _run_validate("cmp_a")
        _run_validate("cmp_b")
        capsys.readouterr()  # drena stdout de validate

        exit_code = cli_app.run(["compare", "cmp_a", "cmp_b"])
        assert exit_code == 0

        out = capsys.readouterr().out
        # Header
        assert "run_a" in out
        assert "run_b" in out
        assert "cmp_a" in out
        assert "cmp_b" in out
        # As quatro seções ADR-0018
        assert "--- run_metadata ---" in out
        assert "--- walk_forward ---" in out
        assert "--- monte_carlo ---" in out
        assert "--- cost_stress ---" in out

    def test_seed_fixo_monte_carlo_percentis_identicos(
        self, redirect_run_dir, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _run_validate("cmp_seed_a")
        _run_validate("cmp_seed_b")
        capsys.readouterr()

        cli_app.run(["compare", "cmp_seed_a", "cmp_seed_b"])
        out = capsys.readouterr().out

        # Mesmo dataset + mesmo seed MC -> percentis identicos -> delta zero em p50.
        # A presenca do bloco monte_carlo com p50 delta zero confirma reprodutibilidade.
        p50_line = next(ln for ln in out.splitlines() if "p50" in ln)
        assert "delta=+0.0000" in p50_line

    def test_skip_flags_substituem_seção_por_marcador_pulado(
        self, redirect_run_dir, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _run_validate("cmp_skip_a")
        _run_validate("cmp_skip_b")
        capsys.readouterr()

        cli_app.run(
            [
                "compare",
                "cmp_skip_a",
                "cmp_skip_b",
                "--skip-walk-forward",
                "--skip-monte-carlo",
            ]
        )
        out = capsys.readouterr().out
        assert "pulado (--skip-walk-forward)" in out
        assert "pulado (--skip-monte-carlo)" in out
        # run_metadata e cost_stress continuam presentes
        assert "alpha_forge_version" in out
        assert "dataset_id" in out

    def test_run_id_inexistente_sai_com_codigo_1(
        self, redirect_run_dir, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _run_validate("cmp_existe")
        capsys.readouterr()

        exit_code = cli_app.run(["compare", "cmp_existe", "cmp_nao_existe"])
        assert exit_code == 1
        err = capsys.readouterr().err
        assert "erro:" in err

    def test_compare_não_altera_artefatos(
        self, redirect_run_dir, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _run_validate("cmp_readonly_a")
        _run_validate("cmp_readonly_b")
        capsys.readouterr()

        dir_a = redirect_run_dir("cmp_readonly_a")
        files = sorted(dir_a.iterdir())
        sizes_antes = {p.name: p.stat().st_size for p in files}
        mtimes_antes = {p.name: p.stat().st_mtime for p in files}

        cli_app.run(["compare", "cmp_readonly_a", "cmp_readonly_b"])
        capsys.readouterr()

        for p in files:
            assert p.stat().st_size == sizes_antes[p.name]
            assert p.stat().st_mtime == mtimes_antes[p.name]

    def test_skip_cost_stress_e_compare_com_corrida_sem_stress(
        self, redirect_run_dir, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # corrida A com stress, corrida B sem — cost_stress ausente em B
        _run_validate("cmp_asym_a")
        # corrida B sem stress
        exit_code = cli_app.run(
            [
                "validate",
                "--run-id",
                "cmp_asym_b",
                "--dataset-id",
                REFERENCE_DATASET_ID,
                "--n-folds",
                "3",
                "--mc-resamples",
                "200",
                "--mc-seed",
                "42",
                "--skip-cost-stress",
            ]
        )
        assert exit_code == 0
        capsys.readouterr()

        cli_app.run(["compare", "cmp_asym_a", "cmp_asym_b"])
        out = capsys.readouterr().out
        # cost_stress presente em A, ausente em B
        assert "presente em A, ausente em B" in out


class TestComparePositionalArgs:
    def test_sem_args_posicionais_erro_de_cli(
        self, redirect_run_dir
    ) -> None:
        with pytest.raises(SystemExit) as exc:
            cli_app.run(["compare"])
        assert exc.value.code == 2

    def test_apenas_um_arg_posicional_erro_de_cli(
        self, redirect_run_dir
    ) -> None:
        with pytest.raises(SystemExit) as exc:
            cli_app.run(["compare", "so_um"])
        assert exc.value.code == 2
