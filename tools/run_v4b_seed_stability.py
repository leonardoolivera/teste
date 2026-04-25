"""V4b (RSI short puro, 2025-H2) seed stability — 4 runs pre-requisito ADR-0068/0069.

CH.7 (BTC 2025-H2) + CH.9 (SOL 2025-H2) SEM regime_filter, seeds {1337, 2024}.
Seed 42 ja em audit-v4-b-*-nofilter (reusa).

Criterio PASS: fails <= 1 em 4 runs.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


COMBOS = [
    ("CH.7", "btc", "20250705_20251231", "btcusdt_1h_20250705_20251231_binance_spot"),
    ("CH.9", "sol", "20250705_20251231", "solusdt_1h_20250705_20251231_binance_spot"),
]


def run_one(run_id: str, dataset_id: str, mc_seed: int) -> None:
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
        "--mc-seed", str(mc_seed),
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--log-level", "silent",
    ]
    print(f"\n{'=' * 70}\n{run_id}\n  no_filter  seed={mc_seed}\n{'=' * 70}")
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for seed in (1337, 2024):
        for tag, asset, suffix, ds in COMBOS:
            rid = f"audit-v4b-nofilter-{asset}-{suffix}-seed{seed}"
            run_one(rid, ds, seed)
    print("\nV4b seed stability completo (4 runs).")
