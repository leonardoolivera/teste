"""Serie CZD -- LINK RSI short replicacao cross-window.

CZ.3 validou LINK 2025-H2 com Sh=1.76. CZD testa se replica em:
- CZD.1: LINK 2025-H1
- CZD.2: LINK 2024-H2

Padrao 24: teste real de robustez via variacao de dataset (janela temporal).

Gate ADR-0105.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PROBES = [
    # (tag, run_id, dataset)
    ("CZD.1", "czd-link-rsi-short-2025h1", "linkusdt_1h_20250105_20250704_binance_spot"),
    ("CZD.2", "czd-link-rsi-short-2024h2", "linkusdt_1h_20240705_20241231_binance_spot"),
]


def run_one(run_id: str, dataset: str) -> None:
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
    for tag, rid, ds in PROBES:
        print(f"\n{'=' * 70}\n{tag} LINK RSI short {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CZD completa (2 runs).")
