"""Rodar BN.1-BN.8: sweep window ∈ {25, 35} × 4 combos do manifest v2.

Mesmo padrão de run_bk_sweep.py, perturbando 'window' ao invés de 'num_std'.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


COMBOS = [
    # (bn_tag, dataset_id, run_id_prefix)
    ("BN.1", "ethusdt_1h_20240105_20240704_binance_spot", "bn-dryrun-w{w}-ns150-bw250-eth-20240105_20240704"),
    ("BN.2", "ethusdt_1h_20250105_20250704_binance_spot", "bn-dryrun-w{w}-ns150-bw250-eth-20250105_20250704"),
    ("BN.3", "btcusdt_1h_20240705_20241231_binance_spot", "bn-dryrun-w{w}-ns150-bw250-btc-20240705_20241231"),
    ("BN.4", "solusdt_1h_20240705_20241231_binance_spot", "bn-dryrun-w{w}-ns150-bw250-sol-20240705_20241231"),
]


def run_one(tag: str, dataset_id: str, run_id: str, window: str) -> None:
    print(f"\n{'=' * 70}\nRunning {tag}: {run_id}\n{'=' * 70}")
    sys.argv = [
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
        "--long-only",
        "--bollinger-window", window,
        "--bollinger-num-std", "1.5",
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--regime-filter", "bollinger_width:min_width_bps=250:num_std=1.5:window=30",
        "--log-level", "silent",
    ]
    cli_main()


if __name__ == "__main__":
    # BN.1-BN.4: w=25
    for tag, ds, rid_fmt in COMBOS:
        run_one(tag, ds, rid_fmt.format(w="25"), "25")
    # BN.5-BN.8: w=35 (re-tag)
    for i, (tag, ds, rid_fmt) in enumerate(COMBOS):
        hi_tag = f"BN.{i + 5}"
        run_one(hi_tag, ds, rid_fmt.format(w="35"), "35")
    print("\nBN.1-BN.8 completo.")
