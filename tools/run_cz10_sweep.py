"""Serie CZ10 -- RSI bounds sensibilidade (25/75, 35/65) (ADR-0134)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


WIDTH_FILTER = "bollinger_width:window=30:num_std=1.5:min_width_bps=250"
TREND_FILTER = "trend_htf:htf=4h:sma_window=50:mode=short_only"

PROBES = [
    ("CZ10.1", "cz10-sol-rsi-2575-naked-1h-2025h2",
     "solusdt_1h_20250705_20251231_binance_spot", 25, 75, None),
    ("CZ10.2", "cz10-sol-rsi-3565-naked-1h-2025h2",
     "solusdt_1h_20250705_20251231_binance_spot", 35, 65, None),
    ("CZ10.3", "cz10-btc-rsi-2575-width-1h-2025h1",
     "btcusdt_1h_20250105_20250704_binance_spot", 25, 75, WIDTH_FILTER),
    ("CZ10.4", "cz10-btc-rsi-3565-width-1h-2025h1",
     "btcusdt_1h_20250105_20250704_binance_spot", 35, 65, WIDTH_FILTER),
    ("CZ10.5", "cz10-sol-rsi-2575-trendhtf-1h-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot", 25, 75, TREND_FILTER),
    ("CZ10.6", "cz10-sol-rsi-3565-trendhtf-1h-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot", 35, 65, TREND_FILTER),
]


def run_one(run_id: str, dataset: str, oversold: int, overbought: int, regime: str | None) -> None:
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
        "--rsi-oversold", str(oversold),
        "--rsi-overbought", str(overbought),
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
    for tag, rid, ds, ob, ovb, rgf in PROBES:
        print(f"\n{'=' * 70}\n{tag} rsi {ob}/{ovb} -- {ds} | filter={rgf}\n{'=' * 70}")
        run_one(rid, ds, ob, ovb, rgf)
    print("\nSerie CZ10 completa (6 runs).")
