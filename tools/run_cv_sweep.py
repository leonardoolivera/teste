"""Serie CV -- RSI long cross-period 2024-H2 + 2025-H2 (6 runs).

Gate pre-registrado em ADR-0089. Testa se RSI long funciona em janelas com drift
positivo (bull 2024-H2, misto 2025-H2). CU ja refutou long em chop 2025-H1.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CV.1", "btcusdt_1h_20240705_20241231_binance_spot", "btc", "2024h2"),
    ("CV.2", "ethusdt_1h_20240705_20241231_binance_spot", "eth", "2024h2"),
    ("CV.3", "solusdt_1h_20240705_20241231_binance_spot", "sol", "2024h2"),
    ("CV.4", "btcusdt_1h_20250705_20251231_binance_spot", "btc", "2025h2"),
    ("CV.5", "ethusdt_1h_20250705_20251231_binance_spot", "eth", "2025h2"),
    ("CV.6", "solusdt_1h_20250705_20251231_binance_spot", "sol", "2025h2"),
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
        rid = f"cv-{prefix}-rsi-long-{win}"
        print(f"\n{'=' * 70}\n{tag} RSI long naked -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CV completa (6 runs).")
