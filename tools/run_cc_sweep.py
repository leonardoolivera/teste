"""Serie CC — Bollinger 20/1.5 + trend_htf cross-period (18 runs).

Gate pre-registrado em ADR-0044. Nao mover regua post-hoc.
9 pilotos filtered (atr_regime AND trend_htf) + 9 baselines (atr_regime only).
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CC.1", "ethusdt_1h_20230705_20231231_binance_spot", "eth", "20230705_20231231", 105),
    ("CC.2", "btcusdt_1h_20230705_20231231_binance_spot", "btc", "20230705_20231231", 55),
    ("CC.3", "solusdt_1h_20230705_20231231_binance_spot", "sol", "20230705_20231231", 100),
    ("CC.4", "ethusdt_1h_20250105_20250704_binance_spot", "eth", "20250105_20250704", 105),
    ("CC.5", "btcusdt_1h_20250105_20250704_binance_spot", "btc", "20250105_20250704", 55),
    ("CC.6", "solusdt_1h_20250105_20250704_binance_spot", "sol", "20250105_20250704", 100),
    ("CC.7", "ethusdt_1h_20250705_20251231_binance_spot", "eth", "20250705_20251231", 105),
    ("CC.8", "btcusdt_1h_20250705_20251231_binance_spot", "btc", "20250705_20251231", 55),
    ("CC.9", "solusdt_1h_20250705_20251231_binance_spot", "sol", "20250705_20251231", 100),
]


def run_one(run_id: str, dataset_id: str, atr_bps: int, with_htf: bool) -> None:
    if with_htf:
        spec = f"and(atr_regime:window=14:min_atr_bps={atr_bps},trend_htf:htf=4h:sma_window=50:mode=long_only)"
    else:
        spec = f"atr_regime:window=14:min_atr_bps={atr_bps}"
    print(f"\n{'=' * 70}\n{run_id}\n  filter={spec}\n{'=' * 70}")
    sys.argv = [
        "alpha-forge", "validate",
        "--run-id", run_id,
        "--dataset-id", dataset_id,
        "--capital", "10000.0",
        "--fracao", "0.1",
        "--alavancagem", "2.0",
        "--taker-fee-bps", "5.0",
        "--slippage-bps-per-notional", "2.0",
        "--spread-bps", "0.0",
        "--strategy", "bollinger",
        "--long-only",
        "--bollinger-window", "20",
        "--bollinger-num-std", "1.5",
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--regime-filter", spec,
        "--log-level", "silent",
    ]
    cli_main()


if __name__ == "__main__":
    for tag, ds, asset, suffix, atr_bps in PILOTS:
        rid_f = f"cc-boll-20-15-{asset}-{suffix}-atr{atr_bps}-htf4h50"
        run_one(rid_f, ds, atr_bps, with_htf=True)
        rid_b = f"cc-boll-20-15-{asset}-{suffix}-atr{atr_bps}-baseline"
        run_one(rid_b, ds, atr_bps, with_htf=False)
    print("\nSerie CC completa (18 runs = 9 filtered + 9 baselines).")
