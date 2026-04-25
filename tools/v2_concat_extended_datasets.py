"""V2 — Concat datasets para janela contínua estendida (Padrão 59 mitigation).

Concatena BTC/ETH/SOL 1h dos semestres disponíveis em janela contínua
2023-H2 + 2024-H1 + 2024-H2 + 2025-H1 + 2025-H2 = 30 meses (~21,840 bars).

Saída: 3 parquets novos em `data/processed/<asset>/1h/` + entries em
`data/datasets.yaml`.

Uso: python tools/v2_concat_extended_datasets.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
YAML = ROOT / "data" / "datasets.yaml"

WINDOWS = ["2023-H2", "2024-H1", "2024-H2", "2025-H1", "2025-H2"]
WINDOW_MAP = {
    "2023-H2": ("20230705", "20231231"),
    "2024-H1": ("20240105", "20240704"),
    "2024-H2": ("20240705", "20241231"),
    "2025-H1": ("20250105", "20250704"),
    "2025-H2": ("20250705", "20251231"),
}


def merge_asset(symbol: str) -> dict:
    sym_low = symbol.lower()
    asset_dir = DATA / symbol / "1h"
    parts = []
    for w in WINDOWS:
        s, e = WINDOW_MAP[w]
        path = asset_dir / f"{sym_low}_1h_{s}_{e}_binance_spot.parquet"
        if not path.exists():
            print(f"  [WARN] missing {path.name}")
            continue
        df = pd.read_parquet(path)
        parts.append(df)
        print(f"  loaded {path.name}: {len(df)} bars [{df.index.min()} -> {df.index.max()}]")
    if not parts:
        raise RuntimeError(f"No parquets para {symbol}")
    merged = pd.concat(parts, axis=0)
    # Dedupe by index (assume sorted)
    merged = merged[~merged.index.duplicated(keep="first")].sort_index()
    print(f"  merged {symbol}: {len(merged)} bars")

    # Output
    out_id = f"{sym_low}_1h_20230705_20251231_binance_spot_concat30m"
    out_path = asset_dir / f"{out_id}.parquet"
    merged.to_parquet(out_path)

    # SHA256
    sha = hashlib.sha256(out_path.read_bytes()).hexdigest()
    rel_path = f"{symbol}/1h/{out_id}.parquet"
    return {
        "dataset_id": out_id,
        "symbol": symbol,
        "timeframe": "1h",
        "path": rel_path,
        "sha256": sha,
        "row_count": len(merged),
        "start_ts": merged.index.min().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_ts": merged.index.max().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "timezone": "UTC",
        "declared_gaps": [],
        "source": "concat_v2_extended",
    }


def append_to_yaml(entries: list[dict]) -> None:
    """Naive append: re-parse yaml content as text and append entries before any blank line at end."""
    import yaml
    current = YAML.read_text()
    # Use yaml lib to load + dump
    parsed = yaml.safe_load(current)
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
    print(f"\nDONE: {len(entries)} concat datasets criados.")


if __name__ == "__main__":
    main()
