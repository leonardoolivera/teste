"""Serie PY Fase 2 -- pyramid v4 aplicado a BB short + width proven combos.

Compliant ADR-0180 invariante #10 (requires_regime_filter).

3 runs:
 PY.4 SOL 2025-H1 BB short 20/1.5 + width(30/1.5/min=300) + pyramid 2x  (baseline Sh=2.71)
 PY.5 ETH 2025-H1 idem                                                   (baseline Sh=2.40)
 PY.6 SOL 2024-H2 idem                                                   (baseline Sh=1.38)
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
    "--strategy", "bollinger",
    "--no-long-only",
    "--bollinger-window", "20",
    "--bollinger-num-std", "1.5",
    "--regime-filter", "bollinger_width:window=30:num_std=1.5:min_width_bps=300",
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
    ("PY.4", "py-sol-bb-short-width300-pyr-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot"),
    ("PY.5", "py-eth-bb-short-width300-pyr-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot"),
    ("PY.6", "py-sol-bb-short-width300-pyr-2024h2",
     "solusdt_1h_20240705_20241231_binance_spot"),
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
    print("\nSerie PY Fase 2 completa (3 runs).")
