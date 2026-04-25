"""Re-rodar BK.1-BK.8 com regime params CORRETOS (manifest 30/1.5).

Origem: ADR-0037. Original (run_bk_sweep.py) usou regime defaults 20/2 — bug.
Output dir: results/validation/bk-rerun-*  (separado do original).
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


COMBOS_LO = [
    ("BK.1", "ethusdt_1h_20240105_20240704_binance_spot", "bk-rerun-w30-ns1.25-bw250-eth-20240105_20240704"),
    ("BK.2", "ethusdt_1h_20250105_20250704_binance_spot", "bk-rerun-w30-ns1.25-bw250-eth-20250105_20250704"),
    ("BK.3", "btcusdt_1h_20240705_20241231_binance_spot", "bk-rerun-w30-ns1.25-bw250-btc-20240705_20241231"),
    ("BK.4", "solusdt_1h_20240705_20241231_binance_spot", "bk-rerun-w30-ns1.25-bw250-sol-20240705_20241231"),
]
COMBOS_HI = [
    ("BK.5", "ethusdt_1h_20240105_20240704_binance_spot", "bk-rerun-w30-ns1.75-bw250-eth-20240105_20240704"),
    ("BK.6", "ethusdt_1h_20250105_20250704_binance_spot", "bk-rerun-w30-ns1.75-bw250-eth-20250105_20250704"),
    ("BK.7", "btcusdt_1h_20240705_20241231_binance_spot", "bk-rerun-w30-ns1.75-bw250-btc-20240705_20241231"),
    ("BK.8", "solusdt_1h_20240705_20241231_binance_spot", "bk-rerun-w30-ns1.75-bw250-sol-20240705_20241231"),
]


def run_one(tag: str, dataset_id: str, run_id: str, num_std: str) -> None:
    print(f"\n{'=' * 70}\nRerun {tag}: {run_id}\n{'=' * 70}")
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
    for tag, ds, rid in COMBOS_LO:
        run_one(tag, ds, rid, "1.25")
    for tag, ds, rid in COMBOS_HI:
        run_one(tag, ds, rid, "1.75")
    print("\nBK rerun completo (8 pilotos).")
