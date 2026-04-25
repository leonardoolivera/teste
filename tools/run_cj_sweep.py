"""Serie CJ -- RSI short + TrendHTF(4h, sma=50, short_only) cross-period (9 runs).

Gate pre-registrado em ADR-0072. Testa se filter direcional HTF compoe com
mean-rev short (Padrao 13: filter alinhado com payoff). Hipotese: recupera
2024-H2 bull onde CH (RSI+width) falhou.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CJ.1", "btcusdt_1h_20240705_20241231_binance_spot", "btc", "20240705_20241231"),
    ("CJ.2", "ethusdt_1h_20240705_20241231_binance_spot", "eth", "20240705_20241231"),
    ("CJ.3", "solusdt_1h_20240705_20241231_binance_spot", "sol", "20240705_20241231"),
    ("CJ.4", "btcusdt_1h_20250105_20250704_binance_spot", "btc", "20250105_20250704"),
    ("CJ.5", "ethusdt_1h_20250105_20250704_binance_spot", "eth", "20250105_20250704"),
    ("CJ.6", "solusdt_1h_20250105_20250704_binance_spot", "sol", "20250105_20250704"),
    ("CJ.7", "btcusdt_1h_20250705_20251231_binance_spot", "btc", "20250705_20251231"),
    ("CJ.8", "ethusdt_1h_20250705_20251231_binance_spot", "eth", "20250705_20251231"),
    ("CJ.9", "solusdt_1h_20250705_20251231_binance_spot", "sol", "20250705_20251231"),
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
        "--strategy", "rsi",
        "--no-long-only",
        "--rsi-period", "14",
        "--rsi-oversold", "30",
        "--rsi-overbought", "70",
        "--regime-filter", "trend_htf:htf=4h:sma_window=50:mode=short_only",
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
        rid = f"cj-rsi-14-30-70-{asset}-{suffix}-trendhtf-4h-50-short"
        print(f"\n{'=' * 70}\n{tag} RSI short + trendhtf-4h-50-short -- {asset} {suffix}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CJ completa (9 runs).")
