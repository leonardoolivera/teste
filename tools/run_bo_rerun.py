"""Re-rodar BO.1-BO.8 com regime params CORRETOS (manifest 30/1.5).

BO ja varia min_width_bps entre {200,300} — esse perturbacao continua.
Origem: ADR-0037. Output dir prefix: bo-rerun-*.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


COMBOS = [
    ("BO.1", "ethusdt_1h_20240105_20240704_binance_spot", "bo-rerun-w30-ns150-bw{bw}-eth-20240105_20240704"),
    ("BO.2", "ethusdt_1h_20250105_20250704_binance_spot", "bo-rerun-w30-ns150-bw{bw}-eth-20250105_20250704"),
    ("BO.3", "btcusdt_1h_20240705_20241231_binance_spot", "bo-rerun-w30-ns150-bw{bw}-btc-20240705_20241231"),
    ("BO.4", "solusdt_1h_20240705_20241231_binance_spot", "bo-rerun-w30-ns150-bw{bw}-sol-20240705_20241231"),
]


def run_one(tag: str, dataset_id: str, run_id: str, bw: str) -> None:
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
        "--bollinger-num-std", "1.5",
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--regime-filter", f"bollinger_width:min_width_bps={bw}:num_std=1.5:window=30",
        "--log-level", "silent",
    ]
    cli_main()


if __name__ == "__main__":
    for tag, ds, rid_fmt in COMBOS:
        run_one(tag, ds, rid_fmt.format(bw="200"), "200")
    for i, (tag, ds, rid_fmt) in enumerate(COMBOS):
        hi_tag = f"BO.{i + 5}"
        run_one(hi_tag, ds, rid_fmt.format(bw="300"), "300")
    print("\nBO rerun completo (8 pilotos).")
