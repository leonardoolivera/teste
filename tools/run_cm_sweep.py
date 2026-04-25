"""Serie CM -- RSI(14/30/70) puro cross-timeframe 4h (3 runs, 2024-H2 only).

Escopo reduzido: unica janela com 4h disponivel. Gate pre-registrado em ADR-0080.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CM.1", "btcusdt_4h_20240705_20241231_binance_spot", "btc"),
    ("CM.2", "ethusdt_4h_20240705_20241231_binance_spot", "eth"),
    ("CM.3", "solusdt_4h_20240705_20241231_binance_spot", "sol"),
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
        "--log-level", "silent",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, ds, asset in PILOTS:
        rid = f"cm-rsi-pure-{asset}-20240705_20241231-4h-short"
        print(f"\n{'=' * 70}\n{tag} RSI puro 4h -- {asset} 2024-H2\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CM completa (3 runs).")
