"""Serie CZ16 -- Bollinger window sensibilidade primeira janela (ADR-0148)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


WIDTH_FILTER_300 = "bollinger_width:window=30:num_std=1.5:min_width_bps=300"
WIDTH_FILTER_250 = "bollinger_width:window=30:num_std=1.5:min_width_bps=250"

PROBES = [
    ("CZ16.1", "cz16-sol-bb-w10-ns1.5-short-width-1h-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot", 10, False, WIDTH_FILTER_300),
    ("CZ16.2", "cz16-sol-bb-w40-ns1.5-short-width-1h-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot", 40, False, WIDTH_FILTER_300),
    ("CZ16.3", "cz16-eth-bb-w10-ns1.5-short-width-1h-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot", 10, False, WIDTH_FILTER_300),
    ("CZ16.4", "cz16-eth-bb-w40-ns1.5-short-width-1h-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot", 40, False, WIDTH_FILTER_300),
    ("CZ16.5", "cz16-sol-bb-w15-ns1.5-long-width-1h-2024h2",
     "solusdt_1h_20240705_20241231_binance_spot", 15, True, WIDTH_FILTER_250),
    ("CZ16.6", "cz16-sol-bb-w45-ns1.5-long-width-1h-2024h2",
     "solusdt_1h_20240705_20241231_binance_spot", 45, True, WIDTH_FILTER_250),
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
        print(f"\n{'=' * 70}\n{tag} BB w={w} long={lo} -- {ds}\n{'=' * 70}")
        run_one(rid, ds, w, lo, rgf)
    print("\nSerie CZ16 completa (6 runs).")
