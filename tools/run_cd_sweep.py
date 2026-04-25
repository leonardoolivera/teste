"""Serie CD — Donchian 20/10 + trend_htf cross-period (18 runs).

Gate pre-registrado em ADR-0046. Nao mover regua post-hoc.
9 pilotos filtered (trend_htf only, sem atr_regime) + 9 baselines (sem filter).
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CD.1", "ethusdt_1h_20230705_20231231_binance_spot", "eth", "20230705_20231231"),
    ("CD.2", "btcusdt_1h_20230705_20231231_binance_spot", "btc", "20230705_20231231"),
    ("CD.3", "solusdt_1h_20230705_20231231_binance_spot", "sol", "20230705_20231231"),
    ("CD.4", "ethusdt_1h_20250105_20250704_binance_spot", "eth", "20250105_20250704"),
    ("CD.5", "btcusdt_1h_20250105_20250704_binance_spot", "btc", "20250105_20250704"),
    ("CD.6", "solusdt_1h_20250105_20250704_binance_spot", "sol", "20250105_20250704"),
    ("CD.7", "ethusdt_1h_20250705_20251231_binance_spot", "eth", "20250705_20251231"),
    ("CD.8", "btcusdt_1h_20250705_20251231_binance_spot", "btc", "20250705_20251231"),
    ("CD.9", "solusdt_1h_20250705_20251231_binance_spot", "sol", "20250705_20251231"),
]


def run_one(run_id: str, dataset_id: str, with_htf: bool) -> None:
    args = [
        "alpha-forge", "validate",
        "--run-id", run_id,
        "--dataset-id", dataset_id,
        "--capital", "10000.0",
        "--fracao", "0.1",
        "--alavancagem", "2.0",
        "--taker-fee-bps", "5.0",
        "--slippage-bps-per-notional", "2.0",
        "--spread-bps", "0.0",
        "--strategy", "donchian",
        "--long-only",
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
        "--log-level", "silent",
    ]
    if with_htf:
        args += ["--regime-filter", "trend_htf:htf=4h:sma_window=50:mode=long_only"]
    spec = "trend_htf:htf=4h:sma_window=50:mode=long_only" if with_htf else "none"
    print(f"\n{'=' * 70}\n{run_id}\n  filter={spec}\n{'=' * 70}")
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, ds, asset, suffix in PILOTS:
        rid_f = f"cd-don-20-10-{asset}-{suffix}-htf4h50"
        run_one(rid_f, ds, with_htf=True)
        rid_b = f"cd-don-20-10-{asset}-{suffix}-baseline"
        run_one(rid_b, ds, with_htf=False)
    print("\nSerie CD completa (18 runs = 9 filtered + 9 baselines).")
