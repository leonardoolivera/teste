"""Serie TF30 -- BB+width 30m cross-window (3 janelas × 3 ativos)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PROBES = [
    ("TF30.1", "tf30-btc-bol-width-20-2-short-30m-2024h2",
     "btcusdt_30m_20240705_20241231_binance_spot"),
    ("TF30.2", "tf30-eth-bol-width-20-2-short-30m-2024h2",
     "ethusdt_30m_20240705_20241231_binance_spot"),
    ("TF30.3", "tf30-sol-bol-width-20-2-short-30m-2024h2",
     "solusdt_30m_20240705_20241231_binance_spot"),
    ("TF30.4", "tf30-btc-bol-width-20-2-short-30m-2025h1",
     "btcusdt_30m_20250105_20250704_binance_spot"),
    ("TF30.5", "tf30-eth-bol-width-20-2-short-30m-2025h1",
     "ethusdt_30m_20250105_20250704_binance_spot"),
    ("TF30.6", "tf30-sol-bol-width-20-2-short-30m-2025h1",
     "solusdt_30m_20250105_20250704_binance_spot"),
    ("TF30.7", "tf30-btc-bol-width-20-2-short-30m-2025h2",
     "btcusdt_30m_20250705_20251231_binance_spot"),
    ("TF30.8", "tf30-eth-bol-width-20-2-short-30m-2025h2",
     "ethusdt_30m_20250705_20251231_binance_spot"),
    ("TF30.9", "tf30-sol-bol-width-20-2-short-30m-2025h2",
     "solusdt_30m_20250705_20251231_binance_spot"),
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
        "--strategy", "bollinger",
        "--no-long-only",
        "--bollinger-window", "20",
        "--bollinger-num-std", "2.0",
        "--regime-filter", "bollinger_width:window=30:num_std=1.5:min_width_bps=250",
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
        print(f"\n{'=' * 70}\n{tag} | {ds} | BB+width 20/2.0 short 30m\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie TF30 completa (9 runs).")
