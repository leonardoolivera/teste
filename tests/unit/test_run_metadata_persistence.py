"""Unit tests para `RunMetadata` + save/load (ADR-0017).

Round-trip bit-a-bit via `__eq__` do pydantic, com timestamp timezone-aware UTC
fixo. Cobre envelope, rejeição de schema_version estrangeiro e validação
pydantic do payload.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError as PydanticValidationError

from alpha_forge.validation import (
    RunMetadata,
    ValidationError,
    load_run_metadata,
    save_run_metadata,
)


def _sample_metadata() -> RunMetadata:
    return RunMetadata(
        alpha_forge_version="0.0.0",
        timestamp_utc=datetime(2026, 4, 17, 12, 30, 45, tzinfo=timezone.utc),
        command="validate",
        run_id="my_run_42",
        flags={
            "dataset_id": "synthetic_btcusdt_1h_seed42",
            "n_folds": "5",
            "skip_monte_carlo": "False",
            "stress": "['fee+10:10:0']",
        },
    )


class TestRunMetadataSchema:
    def test_rejeita_campos_desconhecidos(self) -> None:
        with pytest.raises(PydanticValidationError):
            RunMetadata(
                alpha_forge_version="0.0.0",
                timestamp_utc=datetime.now(timezone.utc),
                command="validate",
                run_id="r",
                flags={},
                host="localhost",  # type: ignore[call-arg]
            )

    def test_rejeita_version_vazia(self) -> None:
        with pytest.raises(PydanticValidationError):
            RunMetadata(
                alpha_forge_version="",
                timestamp_utc=datetime.now(timezone.utc),
                command="validate",
                run_id="r",
                flags={},
            )

    def test_rejeita_run_id_vazio(self) -> None:
        with pytest.raises(PydanticValidationError):
            RunMetadata(
                alpha_forge_version="0.0.0",
                timestamp_utc=datetime.now(timezone.utc),
                command="validate",
                run_id="",
                flags={},
            )

    def test_rejeita_command_vazio(self) -> None:
        with pytest.raises(PydanticValidationError):
            RunMetadata(
                alpha_forge_version="0.0.0",
                timestamp_utc=datetime.now(timezone.utc),
                command="",
                run_id="r",
                flags={},
            )

    def test_flags_vazio_aceito(self) -> None:
        m = RunMetadata(
            alpha_forge_version="0.0.0",
            timestamp_utc=datetime.now(timezone.utc),
            command="validate",
            run_id="r",
            flags={},
        )
        assert m.flags == {}

    def test_model_eh_frozen(self) -> None:
        m = _sample_metadata()
        with pytest.raises(PydanticValidationError):
            m.run_id = "outro"  # type: ignore[misc]


class TestRoundTrip:
    def test_round_trip_bit_a_bit(self, tmp_path: Path) -> None:
        original = _sample_metadata()
        path = save_run_metadata(metadata=original, directory=tmp_path)
        assert path == tmp_path / "run.json"

        recovered = load_run_metadata(directory=tmp_path)
        assert recovered == original
        assert recovered.timestamp_utc.tzinfo is not None

    def test_sobrescreve_arquivo_existente(self, tmp_path: Path) -> None:
        m1 = _sample_metadata()
        save_run_metadata(metadata=m1, directory=tmp_path)
        m2 = m1.model_copy(update={"run_id": "outra_corrida"})
        save_run_metadata(metadata=m2, directory=tmp_path)

        assert load_run_metadata(directory=tmp_path) == m2

    def test_envelope_possui_schema_version_string(self, tmp_path: Path) -> None:
        save_run_metadata(metadata=_sample_metadata(), directory=tmp_path)
        envelope = json.loads((tmp_path / "run.json").read_text(encoding="utf-8"))
        assert envelope["schema_version"] == "1"
        assert "payload" in envelope


class TestErros:
    def test_arquivo_ausente(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_run_metadata(directory=tmp_path)

    def test_envelope_malformado(self, tmp_path: Path) -> None:
        (tmp_path / "run.json").write_text("{oops", encoding="utf-8")
        with pytest.raises(ValidationError):
            load_run_metadata(directory=tmp_path)

    def test_schema_version_incompativel(self, tmp_path: Path) -> None:
        path = tmp_path / "run.json"
        path.write_text(
            json.dumps({"schema_version": "99", "payload": {}}), encoding="utf-8"
        )
        with pytest.raises(ValidationError):
            load_run_metadata(directory=tmp_path)

    def test_payload_viola_schema(self, tmp_path: Path) -> None:
        path = tmp_path / "run.json"
        path.write_text(
            json.dumps(
                {
                    "schema_version": "1",
                    "payload": {"run_id": "x"},  # faltam campos obrigatórios
                }
            ),
            encoding="utf-8",
        )
        with pytest.raises(ValidationError):
            load_run_metadata(directory=tmp_path)
