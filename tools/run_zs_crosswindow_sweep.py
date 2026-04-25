"""Serie ZS Fase 2 -- cross-window validation (ADR-0175).

ETH+SOL passed Fase 1; BTC failed. Testa cross-window 2025-H2 e cross-era 2024-H2.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PROBES = [
    # 2025-H2
    ("ZS.4", "zs-btc-zscore-20-2-short-1h-2025h2",
     "btcusdt_1h_20250705_20251231_binance_spot"),
    ("ZS.5", "zs-eth-zscore-20-2-short-1h-2025h2",
     "ethusdt_1h_20250705_20251231_binance_spot"),
    ("ZS.6", "zs-sol-zscore-20-2-short-1h-2025h2",
     "solusdt_1h_20250705_20251231_binance_spot"),
    # 2024-H2 cross-era
    ("ZS.7", "zs-btc-zscore-20-2-short-1h-2024h2",
     "btcusdt_1h_20240705_20241231_binance_spot"),
    ("ZS.8", "zs-eth-zscore-20-2-short-1h-2024h2",
     "ethusdt_1h_20240705_20241231_binance_spot"),
    ("ZS.9", "zs-sol-zscore-20-2-short-1h-2024h2",
     "solusdt_1h_20240705_20241231_binance_spot"),
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
        "--strategy", "zscore",
        "--no-long-only",
        "--zscore-window", "20",
        "--zscore-threshold", "2.0",
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
        print(f"\n{'=' * 70}\n{tag} | {ds} | zscore 20/2.0 short\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie ZS Fase 2 completa (6 runs cross-window).")
