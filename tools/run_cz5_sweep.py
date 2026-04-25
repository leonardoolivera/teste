"""Serie CZ5 -- RSI short 4h cross-asset BTC+ETH (ADR-0122)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PROBES = [
    ("CZ5.1", "cz5-btc-rsi-short-naked-4h-2024h2",
     "btcusdt_4h_20240705_20241231_binance_spot"),
    ("CZ5.2", "cz5-eth-rsi-short-naked-4h-2024h2",
     "ethusdt_4h_20240705_20241231_binance_spot"),
    ("CZ5.3", "cz5-eth-rsi-short-naked-4h-2025h1",
     "ethusdt_4h_20250105_20250704_binance_spot"),
    ("CZ5.4", "cz5-eth-rsi-short-naked-4h-2025h2",
     "ethusdt_4h_20250705_20251231_binance_spot"),
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
        "--log-level", "info",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, rid, ds in PROBES:
        print(f"\n{'=' * 70}\n{tag} rsi(short) 4h naked -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CZ5 completa (4 runs).")
