"""Serie CZ18 -- RSI period sensibilidade (7, 21 vs canonico 14) (ADR-0152)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


WIDTH_FILTER = "bollinger_width:window=30:num_std=1.5:min_width_bps=300"
TREND_FILTER = "trend_htf:htf=4h:sma_window=50:mode=short_only"

PROBES = [
    ("CZ18.1", "cz18-sol-rsi-3070-p7-naked-1h-2025h2",
     "solusdt_1h_20250705_20251231_binance_spot", 7, 30, 70, None),
    ("CZ18.2", "cz18-sol-rsi-3070-p21-naked-1h-2025h2",
     "solusdt_1h_20250705_20251231_binance_spot", 21, 30, 70, None),
    ("CZ18.3", "cz18-btc-rsi-3070-p7-width-1h-2025h1",
     "btcusdt_1h_20250105_20250704_binance_spot", 7, 30, 70, WIDTH_FILTER),
    ("CZ18.4", "cz18-btc-rsi-3070-p21-width-1h-2025h1",
     "btcusdt_1h_20250105_20250704_binance_spot", 21, 30, 70, WIDTH_FILTER),
    ("CZ18.5", "cz18-sol-rsi-2575-p7-trendhtf-1h-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot", 7, 25, 75, TREND_FILTER),
    ("CZ18.6", "cz18-sol-rsi-2575-p21-trendhtf-1h-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot", 21, 25, 75, TREND_FILTER),
]


def run_one(run_id: str, dataset: str, period: int, oversold: int, overbought: int,
            regime: str | None) -> None:
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
        "--rsi-period", str(period),
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
    for tag, rid, ds, p, ob, ovb, rgf in PROBES:
        print(f"\n{'=' * 70}\n{tag} RSI p={p} {ob}/{ovb} -- {ds}\n{'=' * 70}")
        run_one(rid, ds, p, ob, ovb, rgf)
    print("\nSerie CZ18 completa (6 runs).")
