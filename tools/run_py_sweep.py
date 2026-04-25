"""Serie PY Fase 1 -- pyramid v4 aplicado a edges RSI proven (ADR-0184).

3 runs:
 PY.1 SOL 2025-H1 RSI 25/75 + trend_htf short_only + pyramid
 PY.2 SOL 2025-H2 RSI 30/70 naked + pyramid
 PY.3 BTC 2025-H2 RSI 30/70 naked + pyramid
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


COMMON = [
    "--capital", "10000.0",
    "--fracao", "0.1",  # ignorado em pyramid; schema requer
    "--alavancagem", "2.0",
    "--sizing-mode", "pyramid_equity",
    "--pyramid-max-tranches", "5",
    "--pyramid-tranche-equity-frac", "0.20",
    "--pyramid-rearm-cooldown-bars", "1",
    "--taker-fee-bps", "5.0",
    "--slippage-bps-per-notional", "2.0",
    "--spread-bps", "0.0",
    "--n-folds", "4",
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
    {
        "tag": "PY.1",
        "run_id": "py-sol-rsi-2575-trendhtf-pyr-2025h1",
        "dataset": "solusdt_1h_20250105_20250704_binance_spot",
        "extra": [
            "--strategy", "rsi",
            "--no-long-only",
            "--rsi-period", "14",
            "--rsi-oversold", "25",
            "--rsi-overbought", "75",
            "--regime-filter", "trend_htf:htf=4h:mode=short_only:sma_window=50",
        ],
    },
    {
        "tag": "PY.2",
        "run_id": "py-sol-rsi-3070-naked-pyr-2025h2",
        "dataset": "solusdt_1h_20250705_20251231_binance_spot",
        "extra": [
            "--strategy", "rsi",
            "--no-long-only",
            "--rsi-period", "14",
            "--rsi-oversold", "30",
            "--rsi-overbought", "70",
        ],
    },
    {
        "tag": "PY.3",
        "run_id": "py-btc-rsi-3070-naked-pyr-2025h2",
        "dataset": "btcusdt_1h_20250705_20251231_binance_spot",
        "extra": [
            "--strategy", "rsi",
            "--no-long-only",
            "--rsi-period", "14",
            "--rsi-oversold", "30",
            "--rsi-overbought", "70",
        ],
    },
]


def run_one(probe):
    args = ["alpha-forge", "validate",
            "--run-id", probe["run_id"],
            "--dataset-id", probe["dataset"],
            *COMMON, *probe["extra"]]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for p in PROBES:
        print(f"\n{'=' * 70}\n{p['tag']} | {p['dataset']} | {p['run_id']}\n{'=' * 70}")
        run_one(p)
    print("\nSerie PY Fase 1 completa (3 runs).")
