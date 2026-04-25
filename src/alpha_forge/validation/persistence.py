"""Persistência de relatórios de validação em JSON (ADR-0015).

Três artefatos fixos por `run_id`:
  - `walk_forward.json` — lista de `WalkForwardFold`.
  - `monte_carlo.json` — um `MonteCarloSummary`.
  - `cost_stress.json` — um `CostStressReport`.

Cada arquivo tem envelope `{"schema_version": "1", "payload": ...}`. Schema
version incompatível levanta `ValidationError` — migração entre versões é ADR
separada. Sobrescrita é permitida (testes + CI).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from alpha_forge.validation.schemas import (
    CostStressReport,
    MonteCarloSummary,
    RunMetadata,
    WalkForwardFold,
)
from alpha_forge.validation.walk_forward import ValidationError

_SCHEMA_VERSION = "1"
_WALK_FORWARD_FILENAME = "walk_forward.json"
_MONTE_CARLO_FILENAME = "monte_carlo.json"
_COST_STRESS_FILENAME = "cost_stress.json"
_RUN_METADATA_FILENAME = "run.json"


def _write_envelope(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    envelope = {"schema_version": _SCHEMA_VERSION, "payload": payload}
    path.write_text(json.dumps(envelope), encoding="utf-8")


def _read_envelope(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"artefato de validação não encontrado: {path}")
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(
            f"JSON malformado em {path}: {exc}"
        ) from exc
    if not isinstance(envelope, dict) or "schema_version" not in envelope or "payload" not in envelope:
        raise ValidationError(
            f"envelope inválido em {path}: faltam chaves 'schema_version' e/ou 'payload'"
        )
    version = envelope["schema_version"]
    if version != _SCHEMA_VERSION:
        raise ValidationError(
            f"schema_version incompatível em {path}: lido {version!r}, esperado {_SCHEMA_VERSION!r}. "
            f"Migração entre versões é ADR separada (ADR-0015 §'Alternatives')."
        )
    return envelope["payload"]


def save_walk_forward_folds(
    *, folds: list[WalkForwardFold], directory: Path
) -> Path:
    """Grava `folds` em `directory/walk_forward.json`. Sobrescreve se existir."""
    path = directory / _WALK_FORWARD_FILENAME
    payload = [f.model_dump(mode="json") for f in folds]
    _write_envelope(path, payload)
    return path


def load_walk_forward_folds(*, directory: Path) -> list[WalkForwardFold]:
    """Carrega `directory/walk_forward.json`."""
    path = directory / _WALK_FORWARD_FILENAME
    payload = _read_envelope(path)
    if not isinstance(payload, list):
        raise ValidationError(
            f"payload inválido em {path}: esperado lista, recebido {type(payload).__name__}"
        )
    try:
        return [WalkForwardFold.model_validate(item) for item in payload]
    except PydanticValidationError as exc:
        raise ValidationError(
            f"payload de {path} viola schema WalkForwardFold: {exc}"
        ) from exc


def save_monte_carlo_summary(
    *, summary: MonteCarloSummary, directory: Path
) -> Path:
    """Grava `summary` em `directory/monte_carlo.json`. Sobrescreve se existir."""
    path = directory / _MONTE_CARLO_FILENAME
    _write_envelope(path, summary.model_dump(mode="json"))
    return path


def load_monte_carlo_summary(*, directory: Path) -> MonteCarloSummary:
    """Carrega `directory/monte_carlo.json`."""
    path = directory / _MONTE_CARLO_FILENAME
    payload = _read_envelope(path)
    try:
        return MonteCarloSummary.model_validate(payload)
    except PydanticValidationError as exc:
        raise ValidationError(
            f"payload de {path} viola schema MonteCarloSummary: {exc}"
        ) from exc


def save_cost_stress_report(
    *, report: CostStressReport, directory: Path
) -> Path:
    """Grava `report` em `directory/cost_stress.json`. Sobrescreve se existir."""
    path = directory / _COST_STRESS_FILENAME
    _write_envelope(path, report.model_dump(mode="json"))
    return path


def load_cost_stress_report(*, directory: Path) -> CostStressReport:
    """Carrega `directory/cost_stress.json`."""
    path = directory / _COST_STRESS_FILENAME
    payload = _read_envelope(path)
    try:
        return CostStressReport.model_validate(payload)
    except PydanticValidationError as exc:
        raise ValidationError(
            f"payload de {path} viola schema CostStressReport: {exc}"
        ) from exc


def save_run_metadata(*, metadata: RunMetadata, directory: Path) -> Path:
    """Grava `metadata` em `directory/run.json` (ADR-0017). Sobrescreve se existir."""
    path = directory / _RUN_METADATA_FILENAME
    _write_envelope(path, metadata.model_dump(mode="json"))
    return path


def load_run_metadata(*, directory: Path) -> RunMetadata:
    """Carrega `directory/run.json` (ADR-0017)."""
    path = directory / _RUN_METADATA_FILENAME
    payload = _read_envelope(path)
    try:
        return RunMetadata.model_validate(payload)
    except PydanticValidationError as exc:
        raise ValidationError(
            f"payload de {path} viola schema RunMetadata: {exc}"
        ) from exc
