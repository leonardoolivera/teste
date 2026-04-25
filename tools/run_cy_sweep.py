"""Serie CY -- Donchian breakout family exploration (ADR-0116)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PROBES = [
    ("CY.1", "cy-donchian-btc-2024h2", "btcusdt_1h_20240705_20241231_binance_spot"),
    ("CY.2", "cy-donchian-eth-2024h2", "ethusdt_1h_20240705_20241231_binance_spot"),
    ("CY.3", "cy-donchian-sol-2024h2", "solusdt_1h_20240705_20241231_binance_spot"),
    ("CY.4", "cy-donchian-btc-2025h2", "btcusdt_1h_20250705_20251231_binance_spot"),
    ("CY.5", "cy-donchian-eth-2025h2", "ethusdt_1h_20250705_20251231_binance_spot"),
    ("CY.6", "cy-donchian-sol-2025h2", "solusdt_1h_20250705_20251231_binance_spot"),
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
        "--strategy", "donchian",
        "--long-only",
        "--entry-window", "20",
        "--exit-window", "10",
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
        print(f"\n{'=' * 70}\n{tag} donchian(20/10,long) -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CY completa (6 runs).")
