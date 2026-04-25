"""Serie KE Fase 3 -- Keltner naked em timeframe 4h (ADR-0173, dimens\u00e3o n\u00e3o-explorada).
4h deveria ter ATR mais est\u00e1vel que 1h (menos spikes) \u2014 testa hip\u00f3tese ADR-0170 em
timeframe onde estrutura de vol \u00e9 mais plana."""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PROBES = [
    ("KE.13", "ke-btc-keltner-20-14-20-short-4h-2025h1",
     "btcusdt_4h_20250105_20250704_binance_spot"),
    ("KE.14", "ke-eth-keltner-20-14-20-short-4h-2025h1",
     "ethusdt_4h_20250105_20250704_binance_spot"),
    ("KE.15", "ke-sol-keltner-20-14-20-short-4h-2025h1",
     "solusdt_4h_20250105_20250704_binance_spot"),
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
        "--strategy", "keltner",
        "--no-long-only",
        "--keltner-window", "20",
        "--keltner-atr-period", "14",
        "--keltner-mult", "2.0",
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
        print(f"\n{'=' * 70}\n{tag} | {ds} | Keltner 20/14/2.0 short 4h\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie KE Fase 3 (4h) completa (3 runs).")
