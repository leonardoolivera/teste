"""Serie CZ14 -- Bollinger num_std sensibilidade primeira janela (ADR-0144)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


WIDTH_FILTER_300 = "bollinger_width:window=30:num_std=1.5:min_width_bps=300"
WIDTH_FILTER_250 = "bollinger_width:window=30:num_std=1.5:min_width_bps=250"

PROBES = [
    ("CZ14.1", "cz14-sol-bb-1.2-w20-short-width-1h-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot", 20, 1.2, False, WIDTH_FILTER_300),
    ("CZ14.2", "cz14-sol-bb-2.0-w20-short-width-1h-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot", 20, 2.0, False, WIDTH_FILTER_300),
    ("CZ14.3", "cz14-eth-bb-1.2-w20-short-width-1h-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot", 20, 1.2, False, WIDTH_FILTER_300),
    ("CZ14.4", "cz14-eth-bb-2.0-w20-short-width-1h-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot", 20, 2.0, False, WIDTH_FILTER_300),
    ("CZ14.5", "cz14-sol-bb-1.2-w30-long-width-1h-2024h2",
     "solusdt_1h_20240705_20241231_binance_spot", 30, 1.2, True, WIDTH_FILTER_250),
    ("CZ14.6", "cz14-sol-bb-2.0-w30-long-width-1h-2024h2",
     "solusdt_1h_20240705_20241231_binance_spot", 30, 2.0, True, WIDTH_FILTER_250),
]


def run_one(run_id: str, dataset: str, window: int, num_std: float,
            long_only: bool, regime: str) -> None:
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
        "--bollinger-num-std", str(num_std),
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
    for tag, rid, ds, w, ns, lo, rgf in PROBES:
        print(f"\n{'=' * 70}\n{tag} BB w={w} ns={ns} long={lo} -- {ds}\n{'=' * 70}")
        run_one(rid, ds, w, ns, lo, rgf)
    print("\nSerie CZ14 completa (6 runs).")
