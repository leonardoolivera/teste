"""Serie CT -- RSI short cross-timeframe 4h (ADR-0114)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


WIDTH_FILTER = "bollinger_width:window=30:num_std=1.5:min_width_bps=300"

PROBES = [
    ("CT.1", "ct-v4a-btc-rsi-short-width-4h-2025h1",
     "btcusdt_4h_20250105_20250704_binance_spot", WIDTH_FILTER),
    ("CT.2", "ct-v81-btc-rsi-short-naked-4h-2025h2",
     "btcusdt_4h_20250705_20251231_binance_spot", None),
    ("CT.3", "ct-v81-sol-rsi-short-naked-4h-2025h2",
     "solusdt_4h_20250705_20251231_binance_spot", None),
]


def run_one(run_id: str, dataset: str, rfilter: str | None) -> None:
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
    ]
    if rfilter:
        args += ["--regime-filter", rfilter]
    args += [
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--log-level", "info",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, rid, ds, rf in PROBES:
        print(f"\n{'=' * 70}\n{tag} rsi(short) 4h filter={bool(rf)} -- {ds}\n{'=' * 70}")
        run_one(rid, ds, rf)
    print("\nSerie CT completa (3 runs).")
