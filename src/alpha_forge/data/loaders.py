"""Loader de datasets OHLCV versionados.

Único ponto autorizado a ler `data/datasets.yaml` e produzir DataFrames para
o resto do sistema (ADR-0005). Valida sha256, janela, row_count e continuidade
temporal antes de devolver o DataFrame.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import cast

import pandas as pd
import yaml

from alpha_forge.data.schemas import DatasetManifest, GapRecord
from alpha_forge.data.synthetic import TIMEFRAME_DELTAS
from alpha_forge.io.paths import data_processed_dir, datasets_manifest_path


class DatasetIntegrityError(RuntimeError):
    """Manifesto e arquivo divergem, ou o arquivo tem gaps não declarados."""


class DatasetNotFoundError(KeyError):
    """`dataset_id` ausente do manifesto."""


def _read_manifest_file(path: Path) -> list[DatasetManifest]:
    if not path.exists():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries_raw = raw.get("datasets", [])
    return [DatasetManifest.model_validate(entry) for entry in entries_raw]


def load_manifest(manifest_path: Path | None = None) -> list[DatasetManifest]:
    return _read_manifest_file(manifest_path or datasets_manifest_path())


def find_manifest_entry(
    dataset_id: str, manifest_path: Path | None = None
) -> DatasetManifest:
    for entry in load_manifest(manifest_path):
        if entry.dataset_id == dataset_id:
            return entry
    raise DatasetNotFoundError(dataset_id)


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _timeframe_step(timeframe: str) -> timedelta:
    if timeframe not in TIMEFRAME_DELTAS:
        raise DatasetIntegrityError(
            f"timeframe '{timeframe}' não suportado pelo loader atual"
        )
    return TIMEFRAME_DELTAS[timeframe]


def _undeclared_gaps(
    timestamps: pd.DatetimeIndex,
    step: timedelta,
    declared: list[GapRecord],
) -> list[tuple[datetime, datetime]]:
    """Encontra buracos no índice não cobertos pelos intervalos declarados."""
    if len(timestamps) < 2:
        return []
    deltas = timestamps[1:] - timestamps[:-1]
    expected = pd.Timedelta(step)
    undeclared: list[tuple[datetime, datetime]] = []
    for i, delta in enumerate(deltas):
        if delta == expected:
            continue
        gap_start = cast(pd.Timestamp, timestamps[i] + expected).to_pydatetime()
        gap_end = cast(pd.Timestamp, timestamps[i + 1] - expected).to_pydatetime()
        if not _gap_is_declared(gap_start, gap_end, declared):
            undeclared.append((gap_start, gap_end))
    return undeclared


def _gap_is_declared(
    gap_start: datetime, gap_end: datetime, declared: list[GapRecord]
) -> bool:
    return any(
        rec.start <= gap_start and rec.end >= gap_end for rec in declared
    )


def load_dataset(
    dataset_id: str, manifest_path: Path | None = None
) -> pd.DataFrame:
    """Carrega o dataset validando manifesto, hash, janela e continuidade.

    Falha explícita se o arquivo não bate com o manifesto ou se há gaps não
    declarados (ADR-0005).
    """
    manifest_file = manifest_path or datasets_manifest_path()
    entry = find_manifest_entry(dataset_id, manifest_file)

    parquet_path = (data_processed_dir() / entry.path).resolve()
    if not parquet_path.exists():
        raise DatasetIntegrityError(
            f"dataset '{dataset_id}': arquivo ausente em {parquet_path}"
        )

    actual_sha = sha256_of_file(parquet_path)
    if actual_sha != entry.sha256:
        raise DatasetIntegrityError(
            f"dataset '{dataset_id}': sha256 do arquivo diverge do manifesto "
            f"(esperado {entry.sha256}, encontrado {actual_sha})"
        )

    df = pd.read_parquet(parquet_path)
    if not isinstance(df.index, pd.DatetimeIndex):
        raise DatasetIntegrityError(
            f"dataset '{dataset_id}': index não é DatetimeIndex"
        )
    if df.index.tz is None:
        raise DatasetIntegrityError(
            f"dataset '{dataset_id}': timestamps sem timezone"
        )

    if len(df) != entry.row_count:
        raise DatasetIntegrityError(
            f"dataset '{dataset_id}': row_count diverge "
            f"(manifesto={entry.row_count}, arquivo={len(df)})"
        )

    first_ts = cast(pd.Timestamp, df.index[0]).to_pydatetime()
    last_ts = cast(pd.Timestamp, df.index[-1]).to_pydatetime()
    if first_ts != entry.start_ts:
        raise DatasetIntegrityError(
            f"dataset '{dataset_id}': start_ts diverge "
            f"(manifesto={entry.start_ts}, arquivo={first_ts})"
        )
    if last_ts != entry.end_ts:
        raise DatasetIntegrityError(
            f"dataset '{dataset_id}': end_ts diverge "
            f"(manifesto={entry.end_ts}, arquivo={last_ts})"
        )

    step = _timeframe_step(entry.timeframe)
    undeclared = _undeclared_gaps(
        cast(pd.DatetimeIndex, df.index), step, entry.declared_gaps
    )
    if undeclared:
        preview = ", ".join(f"[{s} → {e}]" for s, e in undeclared[:3])
        raise DatasetIntegrityError(
            f"dataset '{dataset_id}': {len(undeclared)} gap(s) não declarado(s): {preview}"
        )

    return df
