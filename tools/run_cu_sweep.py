"""Serie CU -- RSI long cross-asset BTC/ETH/SOL 2025-H1 (3 runs).

Gate pre-registrado em ADR-0087. Diversificacao stack short-heavy testando RSI long.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CU.1", "btcusdt_1h_20250105_20250704_binance_spot", "btc"),
    ("CU.2", "ethusdt_1h_20250105_20250704_binance_spot", "eth"),
    ("CU.3", "solusdt_1h_20250105_20250704_binance_spot", "sol"),
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
    for tag, ds, prefix in PILOTS:
        rid = f"cu-{prefix}-rsi-long-20250105_20250704"
        print(f"\n{'=' * 70}\n{tag} RSI long naked -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CU completa (3 runs).")
