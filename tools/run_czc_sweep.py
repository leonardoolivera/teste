"""Serie CZC -- DOT Bollinger naked rescue: seed stability + MC robusto.

CZB.1 teve Sh=1.33 com seed=42 mas falhou MC p5 e cost_r. CZC testa:
- CZC.1: seed 1337 (replicacao)
- CZC.2: seed 2024 (replicacao)
- CZC.3: seed 42 com MC 2000 resamples (MC robusto)

Gate ADR-0103.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PROBES = [
    # (tag, run_id, seed, mc_resamples)
    ("CZC.1", "czc-dot-bollinger-short-naked-seed1337", 1337, 1000),
    ("CZC.2", "czc-dot-bollinger-short-naked-seed2024", 2024, 1000),
    ("CZC.3", "czc-dot-bollinger-short-naked-mc2000",    42, 2000),
]

DATASET = "dotusdt_1h_20250705_20251231_binance_spot"


def run_one(run_id: str, seed: int, mc_resamples: int) -> None:
    args = [
        "alpha-forge", "validate",
        "--run-id", run_id,
        "--dataset-id", DATASET,
        "--capital", "10000.0",
        "--fracao", "0.1",
        "--alavancagem", "2.0",
        "--sizing-mode", "fixed_notional",
        "--taker-fee-bps", "5.0",
        "--slippage-bps-per-notional", "2.0",
        "--spread-bps", "0.0",
        "--strategy", "bollinger",
        "--no-long-only",
        "--bollinger-window", "20",
        "--bollinger-num-std", "1.5",
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", str(mc_resamples),
        "--mc-seed", str(seed),
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--log-level", "info",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, rid, seed, mc in PROBES:
        print(f"\n{'=' * 70}\n{tag} Bollinger DOT seed={seed} mc={mc}\n{'=' * 70}")
        run_one(rid, seed, mc)
    print("\nSerie CZC completa (3 runs).")
