"""Serie DE -- trend_htf htf=1d em RSI short 1h (ADR-0167)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


TREND_1D = "trend_htf:htf=1d:sma_window=20:mode=short_only"

PROBES = [
    ("DE.1b", "de-btc-rsi-30-70-trendhtf1d-sma20-short-1h-2025h1",
     "btcusdt_1h_20250105_20250704_binance_spot", 30, 70),
    ("DE.2b", "de-eth-rsi-30-70-trendhtf1d-sma20-short-1h-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot", 30, 70),
    ("DE.3b", "de-sol-rsi-25-75-trendhtf1d-sma20-short-1h-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot", 25, 75),
]


def run_one(run_id: str, dataset: str, oversold: int, overbought: int) -> None:
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
        "--rsi-oversold", str(oversold),
        "--rsi-overbought", str(overbought),
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--regime-filter", TREND_1D,
        "--log-level", "info",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, rid, ds, ov, ob in PROBES:
        print(f"\n{'=' * 70}\n{tag} | {ds} | RSI {ov}/{ob}\n{'=' * 70}")
        run_one(rid, ds, ov, ob)
    print("\nSerie DE completa (3 runs).")
