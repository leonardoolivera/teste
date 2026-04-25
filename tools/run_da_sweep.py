"""Serie DA -- bollinger short + trend_htf filter (3 assets, ADR-0158)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


TREND_FILTER = "trend_htf:htf=4h:sma_window=50:mode=short_only"

PROBES = [
    ("DA.1", "da-btc-bol-w20-ns1.5-trendhtf-short-1h-2025h1",
     "btcusdt_1h_20250105_20250704_binance_spot"),
    ("DA.2", "da-eth-bol-w20-ns1.5-trendhtf-short-1h-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot"),
    ("DA.3", "da-sol-bol-w20-ns1.5-trendhtf-short-1h-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot"),
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
        "--bollinger-num-std", "1.5",
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--regime-filter", TREND_FILTER,
        "--log-level", "info",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, rid, ds in PROBES:
        print(f"\n{'=' * 70}\n{tag} -- {ds} | filter={TREND_FILTER}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie DA completa (3 runs).")
