"""Serie DD -- AVAX cross-window 2025-H2 (ADR-0164 Fase B)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


WIDTH_FILTER = "bollinger_width:window=30:num_std=1.5:min_width_bps=300"
TREND_FILTER = "trend_htf:htf=4h:sma_window=50:mode=short_only"

DS = "avaxusdt_1h_20250705_20251231_binance_spot"

PROBES = [
    ("DD.1", "dd-avax-rsi-30-70-width-short-1h-2025h2", WIDTH_FILTER),
    ("DD.2", "dd-avax-rsi-30-70-trendhtf-short-1h-2025h2", TREND_FILTER),
]


def run_one(run_id: str, regime: str) -> None:
    args = [
        "alpha-forge", "validate",
        "--run-id", run_id,
        "--dataset-id", DS,
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
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--regime-filter", regime,
        "--log-level", "info",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, rid, rgf in PROBES:
        print(f"\n{'=' * 70}\n{tag} | {DS}\nfilter={rgf}\n{'=' * 70}")
        run_one(rid, rgf)
    print("\nSerie DD completa (2 runs).")
