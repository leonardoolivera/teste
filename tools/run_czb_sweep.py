"""Serie CZB -- Bollinger short probe (naked) em DOT/AVAX 2025-H2.

Perna A: probe naked para ver se Bollinger tem naked Sh melhor que RSI.
Se Sh >= 0.5 em algum, rodar perna B (com width filter) em sessao separada.

Gate ADR-0101.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CZB.1", "dotusdt_1h_20250705_20251231_binance_spot", "dot", "2025h2"),
    ("CZB.2", "avaxusdt_1h_20250705_20251231_binance_spot", "avax", "2025h2"),
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
        rid = f"czb-{prefix}-bollinger-short-naked-{win}"
        print(f"\n{'=' * 70}\n{tag} Bollinger(20/1.5) naked short -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CZB Perna A completa (2 runs).")
