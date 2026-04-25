"""Serie ZS Fase 3 -- zscore + bollinger_width filter 2025-H1 (ADR-0175 salvage, Padrão 45)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PROBES = [
    ("ZS.10", "zs-btc-zscore-20-2-short-width-1h-2025h1",
     "btcusdt_1h_20250105_20250704_binance_spot"),
    ("ZS.11", "zs-eth-zscore-20-2-short-width-1h-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot"),
    ("ZS.12", "zs-sol-zscore-20-2-short-width-1h-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot"),
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
        "--regime-filter", "bollinger_width:window=30:num_std=1.5:min_width_bps=300",
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
        print(f"\n{'=' * 70}\n{tag} | {ds} | zscore+width 20/2.0 short\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie ZS Fase 3 completa (3 runs +width).")
