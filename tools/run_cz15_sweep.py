"""Serie CZ15 -- SOL short BB w=20 ns=2.0 cross-window + cross-era (ADR-0146)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


WIDTH_FILTER_300 = "bollinger_width:window=30:num_std=1.5:min_width_bps=300"

PROBES = [
    ("CZ15.1", "cz15-sol-bb-2.0-w20-short-width-1h-2025h2",
     "solusdt_1h_20250705_20251231_binance_spot"),
    ("CZ15.2", "cz15-sol-bb-2.0-w20-short-width-1h-2024h1",
     "solusdt_1h_20240105_20240704_binance_spot"),
    ("CZ15.3", "cz15-sol-bb-2.0-w20-short-width-1h-2024h2",
     "solusdt_1h_20240705_20241231_binance_spot"),
]


def run_one(run_id: str, dataset: str) -> None:
    args = [
        "alpha-forge", "validate",
        "--run-id", run_id,
        "--dataset-id", dataset,
        "--capital", "10000.0",
        "--fracao", "0.1",
        "--alavancagem", "2.0",
        "--sizing-mode", "fixed_notional",
        "--taker-fee-bps", "5.0",
        "--slippage-bps-per-notional", "2.0",
        "--spread-bps", "0.0",
        "--strategy", "bollinger",
        "--no-long-only",
        "--bollinger-window", "20",
        "--bollinger-num-std", "2.0",
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--regime-filter", WIDTH_FILTER_300,
        "--log-level", "info",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, rid, ds in PROBES:
        print(f"\n{'=' * 70}\n{tag} SOL BB ns=2.0 -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CZ15 completa (3 runs).")
