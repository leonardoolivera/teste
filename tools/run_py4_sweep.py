"""Serie PY Fase 4 -- pyramid long em BB long + width proven 2024-H2 (BTC/ETH/SOL)."""
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
    "--strategy", "bollinger",
    "--long-only",
    "--bollinger-window", "30",
    "--bollinger-num-std", "1.5",
    "--regime-filter", "bollinger_width:window=30:num_std=1.5:min_width_bps=250",
    "--n-folds", "3",
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
    ("PY.8",  "py-btc-bb-long-width250-pyr-2024h2",
     "btcusdt_1h_20240705_20241231_binance_spot"),
    ("PY.9",  "py-eth-bb-long-width250-pyr-2024h2",
     "ethusdt_1h_20240705_20241231_binance_spot"),
    ("PY.10", "py-sol-bb-long-width250-pyr-2024h2",
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
    print("\nSerie PY Fase 4 completa (3 runs).")
