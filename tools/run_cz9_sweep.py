"""Serie CZ9 -- MACX 10/30 long naked (ADR-0130)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PROBES = [
    ("CZ9.1", "cz9-btc-macx-1030-long-1h-2024h2", "btcusdt_1h_20240705_20241231_binance_spot"),
    ("CZ9.2", "cz9-eth-macx-1030-long-1h-2024h2", "ethusdt_1h_20240705_20241231_binance_spot"),
    ("CZ9.3", "cz9-sol-macx-1030-long-1h-2024h2", "solusdt_1h_20240705_20241231_binance_spot"),
    ("CZ9.4", "cz9-btc-macx-1030-long-1h-2025h2", "btcusdt_1h_20250705_20251231_binance_spot"),
    ("CZ9.5", "cz9-eth-macx-1030-long-1h-2025h2", "ethusdt_1h_20250705_20251231_binance_spot"),
    ("CZ9.6", "cz9-sol-macx-1030-long-1h-2025h2", "solusdt_1h_20250705_20251231_binance_spot"),
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
        "--short-window", "10",
        "--long-window", "30",
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
        print(f"\n{'=' * 70}\n{tag} macx 10/30 long 1h -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CZ9 completa (6 runs).")
