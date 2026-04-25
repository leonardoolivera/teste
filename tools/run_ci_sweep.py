"""Serie CI -- Donchian short + width (min_width_bps=300) cross-period (9 runs).

Gate pre-registrado em ADR-0070. Testa se padrao 10 (filter composicional eleva edge)
generaliza para terceira familia (breakout) alem de Bollinger e RSI mean-rev.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CI.1", "btcusdt_1h_20240705_20241231_binance_spot", "btc", "20240705_20241231"),
    ("CI.2", "ethusdt_1h_20240705_20241231_binance_spot", "eth", "20240705_20241231"),
    ("CI.3", "solusdt_1h_20240705_20241231_binance_spot", "sol", "20240705_20241231"),
    ("CI.4", "btcusdt_1h_20250105_20250704_binance_spot", "btc", "20250105_20250704"),
    ("CI.5", "ethusdt_1h_20250105_20250704_binance_spot", "eth", "20250105_20250704"),
    ("CI.6", "solusdt_1h_20250105_20250704_binance_spot", "sol", "20250105_20250704"),
    ("CI.7", "btcusdt_1h_20250705_20251231_binance_spot", "btc", "20250705_20251231"),
    ("CI.8", "ethusdt_1h_20250705_20251231_binance_spot", "eth", "20250705_20251231"),
    ("CI.9", "solusdt_1h_20250705_20251231_binance_spot", "sol", "20250705_20251231"),
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
        "--regime-filter", "bollinger_width:window=30:num_std=1.5:min_width_bps=300",
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--log-level", "silent",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, ds, asset, suffix in PILOTS:
        rid = f"ci-donchian-20-10-{asset}-{suffix}-width30-300-short"
        print(f"\n{'=' * 70}\n{tag} Donchian short + width300 -- {asset} {suffix}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CI completa (9 runs).")
