"""Gera o dataset sintético seminal e atualiza `data/datasets.yaml`.

Determinístico: mesma seed, mesmos parâmetros → mesmo Parquet → mesmo sha256.
Seguro para rodar várias vezes; sobrescreve arquivo e entrada de manifesto
com o mesmo `dataset_id` se já existirem.

Uso:
    uv run python scripts/bootstrap_synthetic_dataset.py
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import cast

import pandas as pd
import yaml

from alpha_forge.data.loaders import sha256_of_file
from alpha_forge.data.schemas import DatasetManifest
from alpha_forge.data.synthetic import generate_ohlcv
from alpha_forge.io.paths import (
    data_processed_dir,
    datasets_manifest_path,
    processed_dataset_path,
)


DATASET_ID = "synthetic_btcusdt_1h_seed42"
SYMBOL = "SYNTHBTC"
TIMEFRAME = "1h"
PERIODS = 720  # 30 dias em barras horárias
SEED = 42
START = datetime(2024, 1, 1, tzinfo=timezone.utc)


def main() -> int:
    out_path = processed_dataset_path(SYMBOL, TIMEFRAME, DATASET_ID)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = generate_ohlcv(
        start=START, periods=PERIODS, timeframe=TIMEFRAME, seed=SEED
    )
    df.to_parquet(out_path, engine="pyarrow", compression="snappy")

    sha = sha256_of_file(out_path)
    relative_path = out_path.relative_to(data_processed_dir())
    first_ts = cast(pd.Timestamp, df.index[0]).to_pydatetime()
    last_ts = cast(pd.Timestamp, df.index[-1]).to_pydatetime()

    entry = DatasetManifest(
        dataset_id=DATASET_ID,
        symbol=SYMBOL,
        timeframe=TIMEFRAME,
        path=str(relative_path).replace("\\", "/"),
        sha256=sha,
        row_count=len(df),
        start_ts=first_ts,
        end_ts=last_ts,
        timezone="UTC",
        declared_gaps=[],
        source="synthetic",
    )

    manifest_path = datasets_manifest_path()
    existing = _load_existing(manifest_path)
    updated = [
        e for e in existing if e["dataset_id"] != DATASET_ID
    ] + [entry.model_dump(mode="json")]
    updated.sort(key=lambda e: cast(str, e["dataset_id"]))

    manifest_path.write_text(
        "# Manifesto de datasets (ADR-0005). Versionável no git.\n"
        "# Os arquivos Parquet são regeneráveis via scripts/bootstrap_*.\n\n"
        + yaml.safe_dump({"datasets": updated}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    print(f"[ok] dataset '{DATASET_ID}' gravado em {out_path}")
    print(f"[ok] sha256: {sha}")
    print(f"[ok] manifesto atualizado: {manifest_path}")
    return 0


def _load_existing(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return cast(list[dict[str, object]], raw.get("datasets", []))


if __name__ == "__main__":
    raise SystemExit(main())
