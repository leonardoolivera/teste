"""Serie CX -- Donchian breakout cross-period cross-asset (9 runs).

Gate pre-registrado em ADR-0093. Nova engine family (breakout vs mean-reversion
existentes). Naked, long_only=false (reverse-on-signal ADR-0013).
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CX.1", "btcusdt_1h_20240705_20241231_binance_spot", "btc", "2024h2"),
    ("CX.2", "ethusdt_1h_20240705_20241231_binance_spot", "eth", "2024h2"),
    ("CX.3", "solusdt_1h_20240705_20241231_binance_spot", "sol", "2024h2"),
    ("CX.4", "btcusdt_1h_20250105_20250704_binance_spot", "btc", "2025h1"),
    ("CX.5", "ethusdt_1h_20250105_20250704_binance_spot", "eth", "2025h1"),
    ("CX.6", "solusdt_1h_20250105_20250704_binance_spot", "sol", "2025h1"),
    ("CX.7", "btcusdt_1h_20250705_20251231_binance_spot", "btc", "2025h2"),
    ("CX.8", "ethusdt_1h_20250705_20251231_binance_spot", "eth", "2025h2"),
    ("CX.9", "solusdt_1h_20250705_20251231_binance_spot", "sol", "2025h2"),
]


def run_one(run_id: str, dataset_id: str) -> None:
    args = [
        "alpha-forge", "validate",
        "--run-id", run_id,
        "--dataset-id", dataset_id,
        "--capital", "10000.0",
        "--fracao", "0.1",
        "--alavancagem", "2.0",
        "--sizing-mode", "fixed_notional",
        "--taker-fee-bps", "5.0",
        "--slippage-bps-per-notional", "2.0",
        "--spread-bps", "0.0",
        "--strategy", "donchian",
        "--no-long-only",
        "--entry-window", "20",
        "--exit-window", "10",
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
    for tag, ds, prefix, win in PILOTS:
        rid = f"cx-{prefix}-donchian-20-10-{win}"
        print(f"\n{'=' * 70}\n{tag} Donchian(20,10) naked -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CX completa (9 runs).")
