"""Serie DB -- RSI short + AND(width, trend_htf) composicao (ADR-0160)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


TREND_FILTER = "trend_htf:htf=4h:sma_window=50:mode=short_only"
WIDTH_FILTER = "bollinger_width:window=30:num_std=1.5:min_width_bps=300"
AND_FILTER = f"and({WIDTH_FILTER},{TREND_FILTER})"

PROBES = [
    ("DB.0", "db-btc-rsi-30-70-trendhtf-short-1h-2025h1",
     "btcusdt_1h_20250105_20250704_binance_spot", TREND_FILTER),
    ("DB.1", "db-btc-rsi-30-70-and-width-trendhtf-short-1h-2025h1",
     "btcusdt_1h_20250105_20250704_binance_spot", AND_FILTER),
    ("DB.2", "db-eth-rsi-30-70-and-width-trendhtf-short-1h-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot", AND_FILTER),
    ("DB.3", "db-sol-rsi-30-70-and-width-trendhtf-short-1h-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot", AND_FILTER),
]


def run_one(run_id: str, dataset: str, regime: str) -> None:
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
        "--strategy", "rsi",
        "--no-long-only",
        "--rsi-period", "14",
        "--rsi-oversold", "30",
        "--rsi-overbought", "70",
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--regime-filter", regime,
        "--log-level", "info",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, rid, ds, rgf in PROBES:
        print(f"\n{'=' * 70}\n{tag} -- {ds}\nfilter={rgf}\n{'=' * 70}")
        run_one(rid, ds, rgf)
    print("\nSerie DB completa (4 runs).")
