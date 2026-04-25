"""Serie CZA -- RSI short + width filter rescue em DOT/AVAX 2025-H2.

Pre-registrado ADR-0099. Filter: bollinger_width(30/1.5/300), mesmo que
funcionou em v4a BTC 2025-H1 e v7 ETH 2024-H2 long.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


FILTER = "bollinger_width:window=30:num_std=1.5:min_width_bps=300"

PILOTS = [
    ("CZA.1", "dotusdt_1h_20250705_20251231_binance_spot", "dot", "2025h2"),
    ("CZA.2", "avaxusdt_1h_20250705_20251231_binance_spot", "avax", "2025h2"),
]


def run_one(run_id: str, dataset_id: str) -> None:
    args = [
        "alpha-forge", "validate",
        "--run-id", run_id,
        "--dataset-id", dataset_id,
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
        "--regime-filter", FILTER,
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
    for tag, ds, prefix, win in PILOTS:
        rid = f"cza-{prefix}-rsi-short-width300-{win}"
        print(f"\n{'=' * 70}\n{tag} RSI short + width(300) -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CZA completa (2 runs).")
