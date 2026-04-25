"""Serie CZ13 -- BTC width 25/75 3a janela cross-era 2024 (ADR-0141)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


WIDTH_FILTER = "bollinger_width:window=30:num_std=1.5:min_width_bps=250"

PROBES = [
    ("CZ13.1", "cz13-btc-rsi-2575-width-1h-2024h1",
     "btcusdt_1h_20240105_20240704_binance_spot"),
    ("CZ13.2", "cz13-btc-rsi-2575-width-1h-2024h2",
     "btcusdt_1h_20240705_20241231_binance_spot"),
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
        "--strategy", "rsi",
        "--no-long-only",
        "--rsi-period", "14",
        "--rsi-oversold", "25",
        "--rsi-overbought", "75",
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--regime-filter", WIDTH_FILTER,
        "--log-level", "info",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, rid, ds in PROBES:
        print(f"\n{'=' * 70}\n{tag} rsi 25/75 BTC width -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CZ13 completa (2 runs).")
