"""V2 Cycle 10.C — Concat 10m datasets para janela contínua 18m.

Concatena BTC/ETH/SOL 10m dos 3 semestres disponíveis: 2024-H2, 2025-H1, 2025-H2.
18 meses contínuos = ~78,840 bars cada asset (atende Padrão 60 mínimo 18m).

Saída: 3 parquets novos + entries em datasets.yaml com declared_gaps.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
YAML = ROOT / "data" / "datasets.yaml"

WINDOWS = ["2024-H2", "2025-H1", "2025-H2"]
WINDOW_MAP = {
    "2024-H2": ("20240705", "20241231"),
    "2025-H1": ("20250105", "20250704"),
    "2025-H2": ("20250705", "20251231"),
}


def merge_asset(symbol: str) -> dict:
    sym_low = symbol.lower()
    asset_dir = DATA / symbol / "10m"
    parts = []
    for w in WINDOWS:
        s, e = WINDOW_MAP[w]
        path = asset_dir / f"{sym_low}_10m_{s}_{e}_binance_spot_resampled.parquet"
        if not path.exists():
            print(f"  [WARN] missing {path.name}")
            continue
        df = pd.read_parquet(path)
        parts.append(df)
        print(f"  loaded {path.name}: {len(df)} bars [{df.index.min()} -> {df.index.max()}]")
    if not parts:
        raise RuntimeError(f"No parquets para {symbol}")
    merged = pd.concat(parts, axis=0)
    merged = merged[~merged.index.duplicated(keep="first")].sort_index()
    print(f"  merged {symbol}: {len(merged)} bars")

    out_id = f"{sym_low}_10m_20240705_20251231_binance_spot_concat18m"
    out_path = asset_dir / f"{out_id}.parquet"
    merged.to_parquet(out_path)
    sha = hashlib.sha256(out_path.read_bytes()).hexdigest()
    rel_path = f"{symbol}/10m/{out_id}.parquet"
    return {
        "dataset_id": out_id,
        "symbol": symbol,
        "timeframe": "10m",
        "path": rel_path,
        "sha256": sha,
        "row_count": len(merged),
        "start_ts": merged.index.min().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_ts": merged.index.max().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "timezone": "UTC",
        "declared_gaps": [
            {"start": "2025-01-01T00:00:00Z", "end": "2025-01-04T23:50:00Z"},
        ],
        "source": "concat_v2_10m_extended",
    }


def append_to_yaml(entries: list[dict]) -> None:
    parsed = yaml.safe_load(YAML.read_text())
    existing_ids = {d["dataset_id"] for d in parsed.get("datasets", [])}
    added = 0
    for e in entries:
        if e["dataset_id"] in existing_ids:
            print(f"  [skip] {e['dataset_id']} already in yaml")
            continue
        parsed["datasets"].append(e)
        added += 1
    if added > 0:
        YAML.write_text(yaml.safe_dump(parsed, sort_keys=False, default_flow_style=False))
        print(f"  -> appended {added} entries to datasets.yaml")


def main() -> None:
    entries = []
    for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        print(f"\n=== {sym} ===")
        e = merge_asset(sym)
        entries.append(e)
        print(f"  -> {e['dataset_id']} ({e['row_count']} bars, sha={e['sha256'][:10]}...)")
    append_to_yaml(entries)
    print(f"\nDONE: {len(entries)} concat 10m datasets criados.")


if __name__ == "__main__":
    main()
