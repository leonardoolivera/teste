"""Serie CE — Bollinger + RSI short side cross-period (18 runs).

Gate pre-registrado em ADR-0052. Nao mover regua post-hoc.
3 recortes x 3 ativos x 2 estrategias short-only = 18 pilotos. Sem filtro.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CE.1", "btcusdt_1h_20240705_20241231_binance_spot", "btc", "20240705_20241231"),
    ("CE.2", "ethusdt_1h_20240705_20241231_binance_spot", "eth", "20240705_20241231"),
    ("CE.3", "solusdt_1h_20240705_20241231_binance_spot", "sol", "20240705_20241231"),
    ("CE.4", "btcusdt_1h_20250105_20250704_binance_spot", "btc", "20250105_20250704"),
    ("CE.5", "ethusdt_1h_20250105_20250704_binance_spot", "eth", "20250105_20250704"),
    ("CE.6", "solusdt_1h_20250105_20250704_binance_spot", "sol", "20250105_20250704"),
    ("CE.7", "btcusdt_1h_20250705_20251231_binance_spot", "btc", "20250705_20251231"),
    ("CE.8", "ethusdt_1h_20250705_20251231_binance_spot", "eth", "20250705_20251231"),
    ("CE.9", "solusdt_1h_20250705_20251231_binance_spot", "sol", "20250705_20251231"),
]


def run_bollinger_short(run_id: str, dataset_id: str) -> None:
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
        "--strategy", "bollinger",
        "--no-long-only",
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
        "--log-level", "silent",
    ]
    sys.argv = args
    cli_main()


def run_rsi_short(run_id: str, dataset_id: str) -> None:
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
        "--strategy", "rsi",
        "--no-long-only",
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
        "--log-level", "silent",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, ds, asset, suffix in PILOTS:
        rid_b = f"ce-bol-20-15-{asset}-{suffix}-short"
        print(f"\n{'=' * 70}\n{tag} bollinger short -- {asset} {suffix}\n{'=' * 70}")
        run_bollinger_short(rid_b, ds)
        rid_r = f"ce-rsi-14-30-70-{asset}-{suffix}-short"
        print(f"\n{'=' * 70}\n{tag} rsi short -- {asset} {suffix}\n{'=' * 70}")
        run_rsi_short(rid_r, ds)
    print("\nSerie CE completa (18 runs = 9 bollinger + 9 rsi, short-only).")
