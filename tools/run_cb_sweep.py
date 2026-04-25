"""Serie CB — RSI 14/30/70 cross-period confirmation (9 pilotos).

Gate pre-registrado em ADR-0041. Nao mover regua post-hoc.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CB.1", "ethusdt_1h_20230705_20231231_binance_spot", "eth", "20230705_20231231", 105),
    ("CB.2", "btcusdt_1h_20230705_20231231_binance_spot", "btc", "20230705_20231231", 55),
    ("CB.3", "solusdt_1h_20230705_20231231_binance_spot", "sol", "20230705_20231231", 100),
    ("CB.4", "ethusdt_1h_20250105_20250704_binance_spot", "eth", "20250105_20250704", 105),
    ("CB.5", "btcusdt_1h_20250105_20250704_binance_spot", "btc", "20250105_20250704", 55),
    ("CB.6", "solusdt_1h_20250105_20250704_binance_spot", "sol", "20250105_20250704", 100),
    ("CB.7", "ethusdt_1h_20250705_20251231_binance_spot", "eth", "20250705_20251231", 105),
    ("CB.8", "btcusdt_1h_20250705_20251231_binance_spot", "btc", "20250705_20251231", 55),
    ("CB.9", "solusdt_1h_20250705_20251231_binance_spot", "sol", "20250705_20251231", 100),
]


def run_one(tag: str, dataset_id: str, asset: str, suffix: str, atr_bps: int) -> None:
    run_id = f"cb-rsi-14-30-70-{asset}-{suffix}-atrbps{atr_bps}"
    print(f"\n{'=' * 70}\n{tag}: {run_id}\n{'=' * 70}")
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
        "--strategy", "rsi",
        "--long-only",
        "--rsi-period", "14",
        "--rsi-oversold", "30",
        "--rsi-overbought", "70",
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--regime-filter", f"atr_regime:window=14:min_atr_bps={atr_bps}",
        "--log-level", "silent",
    ]
    cli_main()


if __name__ == "__main__":
    for tag, ds, asset, suffix, atr_bps in PILOTS:
        run_one(tag, ds, asset, suffix, atr_bps)
    print("\nSerie CB completo (9 pilotos).")
