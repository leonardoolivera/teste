"""Serie TF Fase 2 -- BB+width 15m cross-window 2025-H1 + 2025-H2 (ADR-0177)."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PROBES = [
    # 2025-H1
    ("TF.4", "tf-btc-bol-width-20-2-short-15m-2025h1",
     "btcusdt_15m_20250105_20250704_binance_spot"),
    ("TF.5", "tf-eth-bol-width-20-2-short-15m-2025h1",
     "ethusdt_15m_20250105_20250704_binance_spot"),
    ("TF.6", "tf-sol-bol-width-20-2-short-15m-2025h1",
     "solusdt_15m_20250105_20250704_binance_spot"),
    # 2025-H2
    ("TF.7", "tf-btc-bol-width-20-2-short-15m-2025h2",
     "btcusdt_15m_20250705_20251231_binance_spot"),
    ("TF.8", "tf-eth-bol-width-20-2-short-15m-2025h2",
     "ethusdt_15m_20250705_20251231_binance_spot"),
    ("TF.9", "tf-sol-bol-width-20-2-short-15m-2025h2",
     "solusdt_15m_20250705_20251231_binance_spot"),
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
        print(f"\n{'=' * 70}\n{tag} | {ds} | BB+width 20/2.0 short 15m\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie TF Fase 2 completa (6 runs cross-window).")
