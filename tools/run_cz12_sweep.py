"""Serie CZ12 -- RSI 25/75 3a janela SOL 2024-H1 (ADR-0138)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


TREND_FILTER = "trend_htf:htf=4h:sma_window=50:mode=short_only"

PROBES = [
    ("CZ12.1", "cz12-sol-rsi-2575-naked-1h-2024h1",
     "solusdt_1h_20240105_20240704_binance_spot", None),
    ("CZ12.2", "cz12-sol-rsi-2575-trendhtf-1h-2024h1",
     "solusdt_1h_20240105_20240704_binance_spot", TREND_FILTER),
]


def run_one(run_id: str, dataset: str, regime: str | None) -> None:
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
        "--strategy", "rsi",
        "--no-long-only",
        "--rsi-period", "14",
        "--rsi-oversold", "25",
        "--rsi-overbought", "75",
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
    if regime:
        args += ["--regime-filter", regime]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, rid, ds, rgf in PROBES:
        print(f"\n{'=' * 70}\n{tag} rsi 25/75 SOL 2024-H1 -- filter={rgf}\n{'=' * 70}")
        run_one(rid, ds, rgf)
    print("\nSerie CZ12 completa (2 runs).")
