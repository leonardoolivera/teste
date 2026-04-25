"""Rodar BK.2-BK.8: sweep num_std ∈ {1.25, 1.75} × 4 combos do manifest v2.

BK.1 (ETH 2024-H1 × 1.25) já foi rodado separado.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


COMBOS = [
    # (bk_tag, dataset_id, run_id_prefix)
    ("BK.2", "ethusdt_1h_20250105_20250704_binance_spot", "bk-dryrun-w30-ns{ns}-bw250-eth-20250105_20250704"),
    ("BK.3", "btcusdt_1h_20240705_20241231_binance_spot", "bk-dryrun-w30-ns{ns}-bw250-btc-20240705_20241231"),
    ("BK.4", "solusdt_1h_20240705_20241231_binance_spot", "bk-dryrun-w30-ns{ns}-bw250-sol-20240705_20241231"),
]
# BK.5-BK.8 = mesmos 4 combos com ns=1.75. BK.5 = ETH 2024-H1.
COMBOS_HI = [
    ("BK.5", "ethusdt_1h_20240105_20240704_binance_spot", "bk-dryrun-w30-ns{ns}-bw250-eth-20240105_20240704"),
    ("BK.6", "ethusdt_1h_20250105_20250704_binance_spot", "bk-dryrun-w30-ns{ns}-bw250-eth-20250105_20250704"),
    ("BK.7", "btcusdt_1h_20240705_20241231_binance_spot", "bk-dryrun-w30-ns{ns}-bw250-btc-20240705_20241231"),
    ("BK.8", "solusdt_1h_20240705_20241231_binance_spot", "bk-dryrun-w30-ns{ns}-bw250-sol-20240705_20241231"),
]


def run_one(tag: str, dataset_id: str, run_id: str, num_std: str) -> None:
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
        "--bollinger-window", "30",
        "--bollinger-num-std", num_std,
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
    # BK.2-BK.4: ns=1.25 nos outros 3 combos (BK.1 já feito)
    for tag, ds, rid_fmt in COMBOS:
        run_one(tag, ds, rid_fmt.format(ns="1.25"), "1.25")
    # BK.5-BK.8: ns=1.75 nos 4 combos
    for tag, ds, rid_fmt in COMBOS_HI:
        run_one(tag, ds, rid_fmt.format(ns="1.75"), "1.75")
    print("\nBK.2-BK.8 completo.")
