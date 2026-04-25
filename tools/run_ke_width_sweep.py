"""Serie KE Fase 2 -- Keltner short + bollinger_width filter (canonical), 2025-H1."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


WIDTH_FILTER = "bollinger_width:window=30:num_std=1.5:min_width_bps=300"

PROBES = [
    ("KE.10", "ke-btc-keltner-20-14-20-width30-300-short-2025h1",
     "btcusdt_1h_20250105_20250704_binance_spot"),
    ("KE.11", "ke-eth-keltner-20-14-20-width30-300-short-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot"),
    ("KE.12", "ke-sol-keltner-20-14-20-width30-300-short-2025h1",
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
        "--strategy", "keltner",
        "--no-long-only",
        "--keltner-window", "20",
        "--keltner-atr-period", "14",
        "--keltner-mult", "2.0",
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
        print(f"\n{'=' * 70}\n{tag} | {ds} | Keltner 20/14/2.0 short + width(30,1.5,300)\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie KE Fase 2 completa (3 runs).")
