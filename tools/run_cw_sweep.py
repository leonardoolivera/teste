"""Serie CW -- RSI long + bollinger_width filter cross-period (9 runs).

Gate pre-registrado em ADR-0091. Testa se filter resgata RSI long (CU/CV naked FAIL 0/9).
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main

FILTER = "bollinger_width:window=30:num_std=1.5:min_width_bps=300"

PILOTS = [
    ("CW.1", "btcusdt_1h_20240705_20241231_binance_spot", "btc", "2024h2"),
    ("CW.2", "ethusdt_1h_20240705_20241231_binance_spot", "eth", "2024h2"),
    ("CW.3", "solusdt_1h_20240705_20241231_binance_spot", "sol", "2024h2"),
    ("CW.4", "btcusdt_1h_20250105_20250704_binance_spot", "btc", "2025h1"),
    ("CW.5", "ethusdt_1h_20250105_20250704_binance_spot", "eth", "2025h1"),
    ("CW.6", "solusdt_1h_20250105_20250704_binance_spot", "sol", "2025h1"),
    ("CW.7", "btcusdt_1h_20250705_20251231_binance_spot", "btc", "2025h2"),
    ("CW.8", "ethusdt_1h_20250705_20251231_binance_spot", "eth", "2025h2"),
    ("CW.9", "solusdt_1h_20250705_20251231_binance_spot", "sol", "2025h2"),
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
        "--long-only",
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
        rid = f"cw-{prefix}-rsi-long-width300-{win}"
        print(f"\n{'=' * 70}\n{tag} RSI long + width 300 -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CW completa (9 runs).")
