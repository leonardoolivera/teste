"""Serie ST Fase 1 -- SuperTrend trend-follow naked 2025-H1 (BTC/ETH/SOL)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


COMMON = [
    "--capital", "10000.0",
    "--fracao", "0.1",
    "--alavancagem", "2.0",
    "--sizing-mode", "fixed_notional",
    "--taker-fee-bps", "5.0",
    "--slippage-bps-per-notional", "2.0",
    "--spread-bps", "0.0",
    "--strategy", "supertrend",
    "--no-long-only",
    "--supertrend-atr-period", "10",
    "--supertrend-atr-mult", "3.0",
    "--n-folds", "3",
    "--scheme", "rolling",
    "--train-fraction", "0.5",
    "--min-test-bars", "50",
    "--mc-resamples", "1000",
    "--mc-seed", "42",
    "--stress", "fee+10:10:0:0",
    "--stress", "spread+10:0:0:10",
    "--log-level", "info",
]


PROBES = [
    ("ST.1", "st-btc-supertrend-10-3-bi-2025h1",
     "btcusdt_1h_20250105_20250704_binance_spot"),
    ("ST.2", "st-eth-supertrend-10-3-bi-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot"),
    ("ST.3", "st-sol-supertrend-10-3-bi-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot"),
]


def run_one(run_id: str, dataset: str) -> None:
    args = ["alpha-forge", "validate",
            "--run-id", run_id,
            "--dataset-id", dataset,
            *COMMON]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, rid, ds in PROBES:
        print(f"\n{'=' * 70}\n{tag} | {ds} | {rid}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie ST Fase 1 completa (3 runs).")
