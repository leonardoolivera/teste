"""Serie CZ8 -- MACX 20/50 long + bollinger_width(30,1.5,300) (ADR-0128)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PROBES = [
    ("CZ8.1", "cz8-btc-macx-2050-bw300-1h-2024h2", "btcusdt_1h_20240705_20241231_binance_spot"),
    ("CZ8.2", "cz8-eth-macx-2050-bw300-1h-2024h2", "ethusdt_1h_20240705_20241231_binance_spot"),
    ("CZ8.3", "cz8-sol-macx-2050-bw300-1h-2024h2", "solusdt_1h_20240705_20241231_binance_spot"),
    ("CZ8.4", "cz8-btc-macx-2050-bw300-1h-2025h2", "btcusdt_1h_20250705_20251231_binance_spot"),
    ("CZ8.5", "cz8-eth-macx-2050-bw300-1h-2025h2", "ethusdt_1h_20250705_20251231_binance_spot"),
    ("CZ8.6", "cz8-sol-macx-2050-bw300-1h-2025h2", "solusdt_1h_20250705_20251231_binance_spot"),
]

WIDTH_FILTER = "bollinger_width:window=30:num_std=1.5:min_width_bps=300"


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
        "--regime-filter", WIDTH_FILTER,
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
        print(f"\n{'=' * 70}\n{tag} macx 20/50 long + bw(30,1.5,300) -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CZ8 completa (6 runs).")
