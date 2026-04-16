"""Testes do loader: rejeita gap não declarado, sha divergente, row_count errado."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest
import yaml

from alpha_forge.data.loaders import DatasetIntegrityError, load_dataset
from alpha_forge.data.synthetic import generate_ohlcv


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _write_manifest(manifest_path: Path, entries: list[dict[str, object]]) -> None:
    manifest_path.write_text(
        yaml.safe_dump({"datasets": entries}, sort_keys=False), encoding="utf-8"
    )


def _prepare_dataset(tmp_path: Path, df: pd.DataFrame, dataset_id: str) -> Path:
    pq_dir = tmp_path / "data" / "processed" / "SYNTH" / "1h"
    pq_dir.mkdir(parents=True, exist_ok=True)
    pq_path = pq_dir / f"{dataset_id}.parquet"
    df.to_parquet(pq_path, engine="pyarrow", compression="snappy")
    return pq_path


def test_loader_rejeita_gap_nao_declarado(tmp_path, monkeypatch) -> None:
    df = generate_ohlcv(
        start=datetime(2024, 1, 1, tzinfo=timezone.utc), periods=10, seed=1
    )
    df_with_gap = pd.concat([df.iloc[:4], df.iloc[6:]])
    dataset_id = "ds_gap"

    pq_path = _prepare_dataset(tmp_path, df_with_gap, dataset_id)
    manifest_path = tmp_path / "data" / "datasets.yaml"
    _write_manifest(
        manifest_path,
        [
            {
                "dataset_id": dataset_id,
                "symbol": "SYNTH",
                "timeframe": "1h",
                "path": f"SYNTH/1h/{dataset_id}.parquet",
                "sha256": _sha256(pq_path),
                "row_count": len(df_with_gap),
                "start_ts": df_with_gap.index[0].to_pydatetime().isoformat(),
                "end_ts": df_with_gap.index[-1].to_pydatetime().isoformat(),
                "timezone": "UTC",
                "declared_gaps": [],
                "source": "synthetic",
            }
        ],
    )

    _patch_paths(monkeypatch, tmp_path)

    with pytest.raises(DatasetIntegrityError, match="gap"):
        load_dataset(dataset_id, manifest_path=manifest_path)


def test_loader_aceita_gap_declarado(tmp_path, monkeypatch) -> None:
    df = generate_ohlcv(
        start=datetime(2024, 1, 1, tzinfo=timezone.utc), periods=10, seed=2
    )
    df_with_gap = pd.concat([df.iloc[:4], df.iloc[6:]])
    dataset_id = "ds_gap_ok"

    pq_path = _prepare_dataset(tmp_path, df_with_gap, dataset_id)
    manifest_path = tmp_path / "data" / "datasets.yaml"
    gap_start = df.index[4].to_pydatetime().isoformat()
    gap_end = df.index[5].to_pydatetime().isoformat()
    _write_manifest(
        manifest_path,
        [
            {
                "dataset_id": dataset_id,
                "symbol": "SYNTH",
                "timeframe": "1h",
                "path": f"SYNTH/1h/{dataset_id}.parquet",
                "sha256": _sha256(pq_path),
                "row_count": len(df_with_gap),
                "start_ts": df_with_gap.index[0].to_pydatetime().isoformat(),
                "end_ts": df_with_gap.index[-1].to_pydatetime().isoformat(),
                "timezone": "UTC",
                "declared_gaps": [
                    {"start": gap_start, "end": gap_end, "reason": "test"}
                ],
                "source": "synthetic",
            }
        ],
    )

    _patch_paths(monkeypatch, tmp_path)

    out = load_dataset(dataset_id, manifest_path=manifest_path)
    assert len(out) == len(df_with_gap)


def test_loader_rejeita_sha_divergente(tmp_path, monkeypatch) -> None:
    df = generate_ohlcv(
        start=datetime(2024, 1, 1, tzinfo=timezone.utc), periods=8, seed=3
    )
    dataset_id = "ds_sha"
    pq_path = _prepare_dataset(tmp_path, df, dataset_id)
    manifest_path = tmp_path / "data" / "datasets.yaml"
    _write_manifest(
        manifest_path,
        [
            {
                "dataset_id": dataset_id,
                "symbol": "SYNTH",
                "timeframe": "1h",
                "path": f"SYNTH/1h/{dataset_id}.parquet",
                "sha256": "0" * 64,
                "row_count": len(df),
                "start_ts": df.index[0].to_pydatetime().isoformat(),
                "end_ts": df.index[-1].to_pydatetime().isoformat(),
                "timezone": "UTC",
                "declared_gaps": [],
                "source": "synthetic",
            }
        ],
    )

    _patch_paths(monkeypatch, tmp_path)

    with pytest.raises(DatasetIntegrityError, match="sha256"):
        load_dataset(dataset_id, manifest_path=manifest_path)
    del pq_path


def test_loader_multi_asset_nao_colide(tmp_path, monkeypatch) -> None:
    """ADR-0009 §2-bis: dois datasets de símbolos distintos coexistem e
    `load_dataset(dataset_id)` devolve cada um independentemente, sem colisão
    de path."""
    df_a = generate_ohlcv(
        start=datetime(2024, 1, 1, tzinfo=timezone.utc), periods=8, seed=11
    )
    df_b = generate_ohlcv(
        start=datetime(2024, 1, 1, tzinfo=timezone.utc), periods=8, seed=22
    )

    pq_dir_a = tmp_path / "data" / "processed" / "ETHUSDT" / "1h"
    pq_dir_b = tmp_path / "data" / "processed" / "SOLUSDT" / "1h"
    pq_dir_a.mkdir(parents=True, exist_ok=True)
    pq_dir_b.mkdir(parents=True, exist_ok=True)

    id_a = "ethusdt_1h_demo"
    id_b = "solusdt_1h_demo"
    pq_a = pq_dir_a / f"{id_a}.parquet"
    pq_b = pq_dir_b / f"{id_b}.parquet"
    df_a.to_parquet(pq_a, engine="pyarrow", compression="snappy")
    df_b.to_parquet(pq_b, engine="pyarrow", compression="snappy")

    manifest_path = tmp_path / "data" / "datasets.yaml"
    _write_manifest(
        manifest_path,
        [
            {
                "dataset_id": id_a,
                "symbol": "ETHUSDT",
                "timeframe": "1h",
                "path": f"ETHUSDT/1h/{id_a}.parquet",
                "sha256": _sha256(pq_a),
                "row_count": len(df_a),
                "start_ts": df_a.index[0].to_pydatetime().isoformat(),
                "end_ts": df_a.index[-1].to_pydatetime().isoformat(),
                "timezone": "UTC",
                "declared_gaps": [],
                "source": "synthetic",
            },
            {
                "dataset_id": id_b,
                "symbol": "SOLUSDT",
                "timeframe": "1h",
                "path": f"SOLUSDT/1h/{id_b}.parquet",
                "sha256": _sha256(pq_b),
                "row_count": len(df_b),
                "start_ts": df_b.index[0].to_pydatetime().isoformat(),
                "end_ts": df_b.index[-1].to_pydatetime().isoformat(),
                "timezone": "UTC",
                "declared_gaps": [],
                "source": "synthetic",
            },
        ],
    )

    _patch_paths(monkeypatch, tmp_path)

    out_a = load_dataset(id_a, manifest_path=manifest_path)
    out_b = load_dataset(id_b, manifest_path=manifest_path)

    assert len(out_a) == len(df_a)
    assert len(out_b) == len(df_b)
    # Independência: cada dataset tem sua própria sequência (seeds distintos).
    assert not out_a["close"].equals(out_b["close"])


def _patch_paths(monkeypatch, tmp_path: Path) -> None:
    import alpha_forge.data.loaders as loaders_mod

    monkeypatch.setattr(
        loaders_mod, "data_processed_dir", lambda: tmp_path / "data" / "processed"
    )
