"""Serie CP Fase 1 -- composite_bb_rsi short + width em 2025-H1 (BTC/ETH/SOL)."""
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
    "--strategy", "composite_bb_rsi",
    "--no-long-only",
    "--composite-bb-window", "20",
    "--composite-bb-num-std", "1.5",
    "--composite-rsi-period", "14",
    "--composite-rsi-oversold", "35",
    "--composite-rsi-overbought", "65",
    "--regime-filter", "bollinger_width:window=30:num_std=1.5:min_width_bps=300",
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
    ("CP.1", "cp-btc-composite-short-width-2025h1",
     "btcusdt_1h_20250105_20250704_binance_spot"),
    ("CP.2", "cp-eth-composite-short-width-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot"),
    ("CP.3", "cp-sol-composite-short-width-2025h1",
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
    print("\nSerie CP Fase 1 completa (3 runs).")
