"""Serie CZ19 -- width filter internal num_std sensibilidade (ADR-0154)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


def wf(ns_internal: float, min_bps: int) -> str:
    return f"bollinger_width:window=30:num_std={ns_internal}:min_width_bps={min_bps}"


PROBES = [
    ("CZ19.1", "cz19-sol-bb-w20-ns1.5-short-filter-ns1.0-1h-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot", 20, False, wf(1.0, 300)),
    ("CZ19.2", "cz19-sol-bb-w20-ns1.5-short-filter-ns2.0-1h-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot", 20, False, wf(2.0, 300)),
    ("CZ19.3", "cz19-eth-bb-w20-ns1.5-short-filter-ns1.0-1h-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot", 20, False, wf(1.0, 300)),
    ("CZ19.4", "cz19-eth-bb-w20-ns1.5-short-filter-ns2.0-1h-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot", 20, False, wf(2.0, 300)),
    ("CZ19.5", "cz19-sol-bb-w30-ns1.5-long-filter-ns1.0-1h-2024h2",
     "solusdt_1h_20240705_20241231_binance_spot", 30, True, wf(1.0, 250)),
    ("CZ19.6", "cz19-sol-bb-w30-ns1.5-long-filter-ns2.0-1h-2024h2",
     "solusdt_1h_20240705_20241231_binance_spot", 30, True, wf(2.0, 250)),
]


def run_one(run_id: str, dataset: str, window: int, long_only: bool, regime: str) -> None:
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
        "--strategy", "bollinger",
        "--long-only" if long_only else "--no-long-only",
        "--bollinger-window", str(window),
        "--bollinger-num-std", "1.5",
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--regime-filter", regime,
        "--log-level", "info",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, rid, ds, w, lo, rgf in PROBES:
        print(f"\n{'=' * 70}\n{tag} -- {ds} | filter={rgf}\n{'=' * 70}")
        run_one(rid, ds, w, lo, rgf)
    print("\nSerie CZ19 completa (6 runs).")
