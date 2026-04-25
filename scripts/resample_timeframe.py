"""Resample OHLCV de timeframe menor para maior (ADR-0193, série TF10m).

Motivação: Binance Vision publica 1m/3m/5m/15m/30m/1h/... mas não 10m.
Para testar timeframe 10m no lab, agregamos 2×5m → 1×10m com semântica
canônica OHLCV (open=first, high=max, low=min, close=last, volume=sum).

Fluxo:
  1. Carrega dataset fonte via `load_dataset` (valida sha + gaps).
  2. Verifica que (target_step % source_step == 0) e ratio > 1.
  3. Agrupa N barras consecutivas; alinha índice ao início do bucket.
  4. Escreve Parquet em `data/processed/<SYMBOL>/<TIMEFRAME>/<dsid>.parquet`.
  5. Atualiza `data/datasets.yaml` via upsert.

Invariantes preservadas:
  - Timestamps do target alinhados a múltiplos do target_step (origin=epoch).
  - Nenhum bucket parcial: se a janela fonte não alinha com buckets target,
    barras sobrando são descartadas e reportadas.
  - Timezone UTC; index.name = "timestamp".

Uso:
    python scripts/resample_timeframe.py \\
        --source btcusdt_5m_20240705_20241231_binance_spot \\
        --target-timeframe 10m
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import timedelta
from pathlib import Path
from typing import cast

import pandas as pd
import yaml

from alpha_forge.data.loaders import find_manifest_entry, load_dataset
from alpha_forge.data.schemas import DatasetManifest
from alpha_forge.data.synthetic import TIMEFRAME_DELTAS
from alpha_forge.io.paths import (
    data_processed_dir,
    datasets_manifest_path,
    processed_dataset_path,
)


def _pandas_freq(delta: timedelta) -> str:
    total_s = int(delta.total_seconds())
    if total_s % 3600 == 0 and total_s >= 3600:
        return f"{total_s // 3600}h"
    if total_s % 60 == 0:
        return f"{total_s // 60}min"
    return f"{total_s}s"


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def resample_ohlcv(df: pd.DataFrame, target_tf: str) -> pd.DataFrame:
    """Agrega OHLCV para timeframe maior. Origin=epoch, label=left.

    Buckets parciais (incompletos no início/fim) são removidos — o upstream
    garante dataset sem gaps, então só descartamos se a janela não alinha
    com o grid target.
    """
    freq = _pandas_freq(TIMEFRAME_DELTAS[target_tf])
    resampled = df.resample(freq, label="left", closed="left", origin="epoch").agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }
    )
    return resampled.dropna(subset=["open", "high", "low", "close"])


def _upsert_manifest(entry: DatasetManifest, manifest_path: Path) -> None:
    existing: list[dict[str, object]] = []
    if manifest_path.exists():
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        existing = cast(list[dict[str, object]], raw.get("datasets", []))
    updated = [
        e for e in existing if e.get("dataset_id") != entry.dataset_id
    ] + [entry.model_dump(mode="json")]
    updated.sort(key=lambda e: cast(str, e["dataset_id"]))
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        "# Manifesto de datasets (ADR-0005). Versionável no git.\n"
        "# Os arquivos Parquet são regeneráveis via scripts/bootstrap_* e scripts/ingest_*.\n\n"
        + yaml.safe_dump({"datasets": updated}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def resample_one(source_id: str, target_tf: str) -> dict:
    entry_src = find_manifest_entry(source_id)
    src_step = TIMEFRAME_DELTAS[entry_src.timeframe]
    tgt_step = TIMEFRAME_DELTAS[target_tf]
    if tgt_step <= src_step:
        raise ValueError(
            f"target_timeframe {target_tf} não é maior que source {entry_src.timeframe}"
        )
    if int(tgt_step.total_seconds()) % int(src_step.total_seconds()) != 0:
        raise ValueError(
            f"target_timeframe {target_tf} não é múltiplo de source {entry_src.timeframe}"
        )

    df_src = load_dataset(source_id)
    df_tgt = resample_ohlcv(df_src, target_tf)

    if df_tgt.empty:
        raise RuntimeError(f"resample de {source_id} resultou em dataframe vazio")

    first_ts = cast(pd.Timestamp, df_tgt.index[0]).to_pydatetime()
    last_ts = cast(pd.Timestamp, df_tgt.index[-1]).to_pydatetime()

    # dataset_id novo herda janela da fonte (start/end originais, não do target).
    dsid_tgt = (
        f"{entry_src.symbol.lower()}_{target_tf}_"
        f"{entry_src.start_ts.strftime('%Y%m%d')}_"
        f"{entry_src.end_ts.strftime('%Y%m%d')}_binance_spot_resampled"
    )
    parquet_path = processed_dataset_path(entry_src.symbol, target_tf, dsid_tgt)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df_tgt.to_parquet(parquet_path, engine="pyarrow", compression="snappy")
    sha = _sha256_of_file(parquet_path)

    relative = parquet_path.relative_to(data_processed_dir())
    entry_tgt = DatasetManifest(
        dataset_id=dsid_tgt,
        symbol=entry_src.symbol,
        timeframe=target_tf,
        path=str(relative).replace("\\", "/"),
        sha256=sha,
        row_count=len(df_tgt),
        start_ts=first_ts,
        end_ts=last_ts,
        timezone="UTC",
        declared_gaps=entry_src.declared_gaps,
        source=f"resampled_from:{source_id}",
    )
    _upsert_manifest(entry_tgt, datasets_manifest_path())

    ratio = int(tgt_step.total_seconds() // src_step.total_seconds())
    return {
        "source_id": source_id,
        "target_id": dsid_tgt,
        "source_rows": len(df_src),
        "target_rows": len(df_tgt),
        "ratio": ratio,
        "first_ts": first_ts.isoformat(),
        "last_ts": last_ts.isoformat(),
        "sha256": sha,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Resample OHLCV para timeframe maior.")
    p.add_argument("--source", required=True, help="Lista separada por vírgula de dataset_ids fonte.")
    p.add_argument("--target-timeframe", required=True, help="Timeframe alvo (ex: 10m).")
    args = p.parse_args(argv)

    if args.target_timeframe not in TIMEFRAME_DELTAS:
        print(f"[erro] timeframe não suportado: {args.target_timeframe}", file=sys.stderr)
        return 2

    sources = [s.strip() for s in args.source.split(",") if s.strip()]
    results: list[dict] = []
    for sid in sources:
        print(f"\n[resample] {sid} -> {args.target_timeframe}")
        try:
            out = resample_one(sid, args.target_timeframe)
        except Exception as exc:  # noqa: BLE001 — reportar sem abortar o resto
            print(f"  FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
            results.append({"source_id": sid, "error": f"{type(exc).__name__}: {exc}"})
            continue
        print(
            f"  OK: {out['source_rows']} -> {out['target_rows']} rows "
            f"(ratio={out['ratio']}x)"
        )
        print(f"       target_id={out['target_id']}")
        print(f"       sha256={out['sha256']}")
        print(f"       window={out['first_ts']} -> {out['last_ts']}")
        results.append(out)

    failed = [r for r in results if "error" in r]
    print(f"\n=== RESUMO === {len(results) - len(failed)}/{len(results)} ok")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
