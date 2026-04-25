"""Serie CZ6 -- MA Crossover 20/50 long family exploration (ADR-0124)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PROBES = [
    ("CZ6.1", "cz6-btc-macx-2050-long-1h-2024h2", "btcusdt_1h_20240705_20241231_binance_spot"),
    ("CZ6.2", "cz6-eth-macx-2050-long-1h-2024h2", "ethusdt_1h_20240705_20241231_binance_spot"),
    ("CZ6.3", "cz6-sol-macx-2050-long-1h-2024h2", "solusdt_1h_20240705_20241231_binance_spot"),
    ("CZ6.4", "cz6-btc-macx-2050-long-1h-2025h2", "btcusdt_1h_20250705_20251231_binance_spot"),
    ("CZ6.5", "cz6-eth-macx-2050-long-1h-2025h2", "ethusdt_1h_20250705_20251231_binance_spot"),
    ("CZ6.6", "cz6-sol-macx-2050-long-1h-2025h2", "solusdt_1h_20250705_20251231_binance_spot"),
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
        "--strategy", "ma_crossover",
        "--long-only",
        "--short-window", "20",
        "--long-window", "50",
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
        print(f"\n{'=' * 70}\n{tag} macx 20/50 long 1h -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CZ6 completa (6 runs).")
