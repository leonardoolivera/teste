"""Serie PY Fase 3 -- pyramid v4 em zscore+width SOL 2025-H1 (confirmatoria Padrao 48).

Compliant ADR-0180 invariante #10. 1 run unico confirmatorio.

PY.7 SOL 2025-H1 zscore 20/2.0 short + bollinger_width 30/1.5/300 + pyramid 2x
  Baseline ZS.12 (ADR-0176): Sh=4.94, PnL=33.84%, trades=82.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


COMMON = [
    "--capital", "10000.0",
    "--fracao", "0.1",
    "--alavancagem", "2.0",
    "--sizing-mode", "pyramid_equity",
    "--pyramid-max-tranches", "5",
    "--pyramid-tranche-equity-frac", "0.20",
    "--pyramid-rearm-cooldown-bars", "1",
    "--taker-fee-bps", "5.0",
    "--slippage-bps-per-notional", "2.0",
    "--spread-bps", "0.0",
    "--strategy", "zscore",
    "--no-long-only",
    "--zscore-window", "20",
    "--zscore-threshold", "2.0",
    "--regime-filter", "bollinger_width:window=30:num_std=1.5:min_width_bps=300",
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


PROBES = [
    ("PY.7", "py-sol-zscore-short-width300-pyr-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot"),
]


def run_one(run_id: str, dataset: str) -> None:
    args = ["alpha-forge", "validate",
            "--run-id", run_id,
            "--dataset-id", dataset,
            *COMMON]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, rid, ds in PROBES:
        print(f"\n{'=' * 70}\n{tag} | {ds} | {rid}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie PY Fase 3 completa (1 run confirmatorio).")
