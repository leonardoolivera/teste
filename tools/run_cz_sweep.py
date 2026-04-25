"""Serie CZ -- RSI short naked em altcoins (DOT/AVAX/LINK 2025-H2).

Testa se Padrao 20 (crypto major 1h naked: so short-side tem edge) vale
universal em crypto ou se e restrito a majors. Gate pre-registrado ADR-0097.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CZ.1", "dotusdt_1h_20250705_20251231_binance_spot", "dot", "2025h2"),
    ("CZ.2", "avaxusdt_1h_20250705_20251231_binance_spot", "avax", "2025h2"),
    ("CZ.3", "linkusdt_1h_20250705_20251231_binance_spot", "link", "2025h2"),
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
        "--log-level", "info",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, ds, prefix, win in PILOTS:
        rid = f"cz-{prefix}-rsi-short-naked-{win}"
        print(f"\n{'=' * 70}\n{tag} RSI(14/30/70) naked -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CZ completa (3 runs).")
