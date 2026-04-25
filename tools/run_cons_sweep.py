"""Serie CONS Fase 1 -- BB short + max_width=200 + pyramid_equity (ADR-0181).

3 runs probe cheap: BTC/ETH/SOL 1h 2025-H1.
Engine: bollinger 20/2.0 short (no-long-only).
Filter: bollinger_width:window=30:num_std=1.5:min_width_bps=0:max_width_bps=200.
Sizing: pyramid_equity, 5 tranches x 20% equity, alavancagem 5x, rearm 1h.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PROBES = [
    ("CONS.1", "cons-btc-bol-short-maxwidth-pyr-2025h1",
     "btcusdt_1h_20250105_20250704_binance_spot"),
    ("CONS.2", "cons-eth-bol-short-maxwidth-pyr-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot"),
    ("CONS.3", "cons-sol-bol-short-maxwidth-pyr-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot"),
]


def run_one(run_id: str, dataset: str) -> None:
    args = [
        "alpha-forge", "validate",
        "--run-id", run_id,
        "--dataset-id", dataset,
        "--capital", "10000.0",
        "--fracao", "0.1",  # ignorado em pyramid mas schema exige
        "--alavancagem", "5.0",
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
        "--bollinger-num-std", "2.0",
        "--regime-filter",
        "bollinger_width:window=30:num_std=1.5:min_width_bps=0:max_width_bps=200",
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
        print(f"\n{'=' * 70}\n{tag} | {ds} | CONS BB short max_width=200 pyramid 5x20%\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CONS Fase 1 completa (3 runs).")
