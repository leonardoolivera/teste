"""Serie CF — Bollinger short + BollingerWidthFilter cross-period (9 runs).

Gate pre-registrado em ADR-0054. Reusa CE runs existentes como baseline (sem rodar).
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CF.1", "btcusdt_1h_20240705_20241231_binance_spot", "btc", "20240705_20241231"),
    ("CF.2", "ethusdt_1h_20240705_20241231_binance_spot", "eth", "20240705_20241231"),
    ("CF.3", "solusdt_1h_20240705_20241231_binance_spot", "sol", "20240705_20241231"),
    ("CF.4", "btcusdt_1h_20250105_20250704_binance_spot", "btc", "20250105_20250704"),
    ("CF.5", "ethusdt_1h_20250105_20250704_binance_spot", "eth", "20250105_20250704"),
    ("CF.6", "solusdt_1h_20250105_20250704_binance_spot", "sol", "20250105_20250704"),
    ("CF.7", "btcusdt_1h_20250705_20251231_binance_spot", "btc", "20250705_20251231"),
    ("CF.8", "ethusdt_1h_20250705_20251231_binance_spot", "eth", "20250705_20251231"),
    ("CF.9", "solusdt_1h_20250705_20251231_binance_spot", "sol", "20250705_20251231"),
]


def run_one(run_id: str, dataset_id: str) -> None:
    args = [
        "alpha-forge", "validate",
        "--run-id", run_id,
        "--dataset-id", dataset_id,
        "--capital", "10000.0",
        "--fracao", "0.1",
        "--alavancagem", "2.0",
        "--taker-fee-bps", "5.0",
        "--slippage-bps-per-notional", "2.0",
        "--spread-bps", "0.0",
        "--strategy", "bollinger",
        "--no-long-only",
        "--bollinger-window", "20",
        "--bollinger-num-std", "1.5",
        "--regime-filter", "bollinger_width:window=30:num_std=1.5:min_width_bps=250",
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--log-level", "silent",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, ds, asset, suffix in PILOTS:
        rid = f"cf-bol-20-15-{asset}-{suffix}-width30-250-short"
        print(f"\n{'=' * 70}\n{tag} bollinger short + width -- {asset} {suffix}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CF completa (9 runs).")
