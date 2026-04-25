"""Serie CZB Perna B -- Bollinger short + width(300) DOT/AVAX 2025-H2.

Disparada pela Perna A (DOT naked Sh=1.33 >= 0.5 gate). AVAX incluido
como controle mesmo com naked -0.16 (baseline comparativo).

Gate ADR-0101.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CZB.3", "dotusdt_1h_20250705_20251231_binance_spot", "dot", "2025h2"),
    ("CZB.4", "avaxusdt_1h_20250705_20251231_binance_spot", "avax", "2025h2"),
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
        "--strategy", "bollinger",
        "--no-long-only",
        "--bollinger-window", "20",
        "--bollinger-num-std", "1.5",
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
    for tag, ds, prefix, win in PILOTS:
        rid = f"czb-{prefix}-bollinger-short-width300-{win}"
        print(f"\n{'=' * 70}\n{tag} Bollinger + width300 -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CZB Perna B completa (2 runs).")
