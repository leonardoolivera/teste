"""Roadmap batch runner — executa um batch de N probes do roadmap_1000.

Uso: python tools/run_roadmap_batch.py <batch_id>

Onde batch_id identifica um batch custom (MA01, MA02, etc.) mapeado internamente.
Cada batch = 10 probes, ~100min compute.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


DATASETS = {
    "BTC": {
        "2024-H2": "btcusdt_1h_20240705_20241231_binance_spot",
        "2025-H1": "btcusdt_1h_20250105_20250704_binance_spot",
        "2025-H2": "btcusdt_1h_20250705_20251231_binance_spot",
        "10m-2024-H2": "btcusdt_10m_20240705_20241231_binance_spot_resampled",
        "10m-2025-H1": "btcusdt_10m_20250105_20250704_binance_spot_resampled",
        "10m-2025-H2": "btcusdt_10m_20250705_20251231_binance_spot_resampled",
    },
    "ETH": {
        "2024-H2": "ethusdt_1h_20240705_20241231_binance_spot",
        "2025-H1": "ethusdt_1h_20250105_20250704_binance_spot",
        "2025-H2": "ethusdt_1h_20250705_20251231_binance_spot",
        "10m-2024-H2": "ethusdt_10m_20240705_20241231_binance_spot_resampled",
        "10m-2025-H1": "ethusdt_10m_20250105_20250704_binance_spot_resampled",
        "10m-2025-H2": "ethusdt_10m_20250705_20251231_binance_spot_resampled",
    },
    "SOL": {
        "2024-H2": "solusdt_1h_20240705_20241231_binance_spot",
        "2025-H1": "solusdt_1h_20250105_20250704_binance_spot",
        "2025-H2": "solusdt_1h_20250705_20251231_binance_spot",
        "10m-2024-H2": "solusdt_10m_20240705_20241231_binance_spot_resampled",
        "10m-2025-H1": "solusdt_10m_20250105_20250704_binance_spot_resampled",
        "10m-2025-H2": "solusdt_10m_20250705_20251231_binance_spot_resampled",
    },
    "DOT": {
        "2025-H1": "dotusdt_1h_20250105_20250704_binance_spot",
        "2025-H2": "dotusdt_1h_20250705_20251231_binance_spot",
    },
    "LINK": {
        "2025-H1": "linkusdt_1h_20250105_20250704_binance_spot",
        "2025-H2": "linkusdt_1h_20250705_20251231_binance_spot",
    },
    "AVAX": {
        "2025-H1": "avaxusdt_1h_20250105_20250704_binance_spot",
        "2025-H2": "avaxusdt_1h_20250705_20251231_binance_spot",
    },
}


BASE_ARGS_1H = [
    "alpha-forge", "validate",
    "--capital", "10000.0",
    "--fracao", "0.1",
    "--alavancagem", "2.0",
    "--sizing-mode", "fixed_notional",
    "--taker-fee-bps", "5.0",
    "--slippage-bps-per-notional", "2.0",
    "--spread-bps", "0.0",
    "--n-folds", "5",
    "--scheme", "rolling",
    "--train-fraction", "0.5",
    "--min-test-bars", "50",
    "--mc-resamples", "500",
    "--mc-seed", "42",
    "--log-level", "silent",
]


def run(run_id: str, dataset: str, engine_args: list[str]) -> None:
    sys.argv = BASE_ARGS_1H + ["--run-id", run_id, "--dataset-id", dataset] + engine_args
    cli_main()


# =====================================================================
# BATCH DEFINITIONS
# =====================================================================
# MA01 = T1-MA entries 1-10 (ma_crossover 10/30 + 15/45 partial) 10m Padrão 50 cross-era
MA01 = [
    {"id": "MA01.01", "rid": "t1ma-10-30-eth-2024h2-long-10m", "params": ("ma_crossover", 10, 30), "asset": "ETH", "window": "10m-2024-H2"},
    {"id": "MA01.02", "rid": "t1ma-10-30-eth-2025h1-long-10m", "params": ("ma_crossover", 10, 30), "asset": "ETH", "window": "10m-2025-H1"},
    {"id": "MA01.03", "rid": "t1ma-10-30-eth-2025h2-long-10m", "params": ("ma_crossover", 10, 30), "asset": "ETH", "window": "10m-2025-H2"},
    {"id": "MA01.04", "rid": "t1ma-10-30-sol-2024h2-long-10m", "params": ("ma_crossover", 10, 30), "asset": "SOL", "window": "10m-2024-H2"},
    {"id": "MA01.05", "rid": "t1ma-10-30-sol-2025h1-long-10m", "params": ("ma_crossover", 10, 30), "asset": "SOL", "window": "10m-2025-H1"},
    {"id": "MA01.06", "rid": "t1ma-10-30-sol-2025h2-long-10m", "params": ("ma_crossover", 10, 30), "asset": "SOL", "window": "10m-2025-H2"},
    {"id": "MA01.07", "rid": "t1ma-15-45-eth-2024h2-long-10m", "params": ("ma_crossover", 15, 45), "asset": "ETH", "window": "10m-2024-H2"},
    {"id": "MA01.08", "rid": "t1ma-15-45-eth-2025h1-long-10m", "params": ("ma_crossover", 15, 45), "asset": "ETH", "window": "10m-2025-H1"},
    {"id": "MA01.09", "rid": "t1ma-15-45-eth-2025h2-long-10m", "params": ("ma_crossover", 15, 45), "asset": "ETH", "window": "10m-2025-H2"},
    {"id": "MA01.10", "rid": "t1ma-15-45-sol-2024h2-long-10m", "params": ("ma_crossover", 15, 45), "asset": "SOL", "window": "10m-2024-H2"},
]


# MA02 = completar 15/45 SOL + grid 25/75 ETH/SOL × 3 windows + 30/90 bear 2025-H1
MA02 = [
    {"id": "MA02.01", "rid": "t1ma-15-45-sol-2025h1-long-10m", "params": ("ma_crossover", 15, 45), "asset": "SOL", "window": "10m-2025-H1"},
    {"id": "MA02.02", "rid": "t1ma-15-45-sol-2025h2-long-10m", "params": ("ma_crossover", 15, 45), "asset": "SOL", "window": "10m-2025-H2"},
    {"id": "MA02.03", "rid": "t1ma-25-75-eth-2024h2-long-10m", "params": ("ma_crossover", 25, 75), "asset": "ETH", "window": "10m-2024-H2"},
    {"id": "MA02.04", "rid": "t1ma-25-75-eth-2025h1-long-10m", "params": ("ma_crossover", 25, 75), "asset": "ETH", "window": "10m-2025-H1"},
    {"id": "MA02.05", "rid": "t1ma-25-75-eth-2025h2-long-10m", "params": ("ma_crossover", 25, 75), "asset": "ETH", "window": "10m-2025-H2"},
    {"id": "MA02.06", "rid": "t1ma-25-75-sol-2024h2-long-10m", "params": ("ma_crossover", 25, 75), "asset": "SOL", "window": "10m-2024-H2"},
    {"id": "MA02.07", "rid": "t1ma-25-75-sol-2025h1-long-10m", "params": ("ma_crossover", 25, 75), "asset": "SOL", "window": "10m-2025-H1"},
    {"id": "MA02.08", "rid": "t1ma-25-75-sol-2025h2-long-10m", "params": ("ma_crossover", 25, 75), "asset": "SOL", "window": "10m-2025-H2"},
    {"id": "MA02.09", "rid": "t1ma-30-90-eth-2025h1-long-10m", "params": ("ma_crossover", 30, 90), "asset": "ETH", "window": "10m-2025-H1"},
    {"id": "MA02.10", "rid": "t1ma-30-90-sol-2025h1-long-10m", "params": ("ma_crossover", 30, 90), "asset": "SOL", "window": "10m-2025-H1"},
]


# ST01 = supertrend bear-avoidance param robustness 10m em ETH/SOL 2025-H1
# Testa se Padrão 50 é MA-specific ou momentum-general.
ST01 = [
    {"id": "ST01.01", "rid": "t1st-10-2-eth-2025h1-bi-10m", "params": ("supertrend", 10, 2.0, "bi"), "asset": "ETH", "window": "10m-2025-H1"},
    {"id": "ST01.02", "rid": "t1st-10-2-sol-2025h1-bi-10m", "params": ("supertrend", 10, 2.0, "bi"), "asset": "SOL", "window": "10m-2025-H1"},
    {"id": "ST01.03", "rid": "t1st-10-4-eth-2025h1-bi-10m", "params": ("supertrend", 10, 4.0, "bi"), "asset": "ETH", "window": "10m-2025-H1"},
    {"id": "ST01.04", "rid": "t1st-10-4-sol-2025h1-bi-10m", "params": ("supertrend", 10, 4.0, "bi"), "asset": "SOL", "window": "10m-2025-H1"},
    {"id": "ST01.05", "rid": "t1st-14-3-eth-2025h1-bi-10m", "params": ("supertrend", 14, 3.0, "bi"), "asset": "ETH", "window": "10m-2025-H1"},
    {"id": "ST01.06", "rid": "t1st-14-3-sol-2025h1-bi-10m", "params": ("supertrend", 14, 3.0, "bi"), "asset": "SOL", "window": "10m-2025-H1"},
    {"id": "ST01.07", "rid": "t1st-10-3-eth-2025h1-long-10m", "params": ("supertrend", 10, 3.0, "long"), "asset": "ETH", "window": "10m-2025-H1"},
    {"id": "ST01.08", "rid": "t1st-10-3-sol-2025h1-long-10m", "params": ("supertrend", 10, 3.0, "long"), "asset": "SOL", "window": "10m-2025-H1"},
    {"id": "ST01.09", "rid": "t1st-20-3-eth-2025h1-bi-10m", "params": ("supertrend", 20, 3.0, "bi"), "asset": "ETH", "window": "10m-2025-H1"},
    {"id": "ST01.10", "rid": "t1st-20-3-sol-2025h1-bi-10m", "params": ("supertrend", 20, 3.0, "bi"), "asset": "SOL", "window": "10m-2025-H1"},
]


# BT01 = BTC cross-era validation com sweet-spot params MA+ST (Padrão 50 BTC test)
BT01 = [
    {"id": "BT01.01", "rid": "t1ma-25-75-btc-2024h2-long-10m", "params": ("ma_crossover", 25, 75), "asset": "BTC", "window": "10m-2024-H2"},
    {"id": "BT01.02", "rid": "t1ma-25-75-btc-2025h1-long-10m", "params": ("ma_crossover", 25, 75), "asset": "BTC", "window": "10m-2025-H1"},
    {"id": "BT01.03", "rid": "t1ma-25-75-btc-2025h2-long-10m", "params": ("ma_crossover", 25, 75), "asset": "BTC", "window": "10m-2025-H2"},
    {"id": "BT01.04", "rid": "t1st-10-4-btc-2024h2-bi-10m", "params": ("supertrend", 10, 4.0, "bi"), "asset": "BTC", "window": "10m-2024-H2"},
    {"id": "BT01.05", "rid": "t1st-10-4-btc-2025h1-bi-10m", "params": ("supertrend", 10, 4.0, "bi"), "asset": "BTC", "window": "10m-2025-H1"},
    {"id": "BT01.06", "rid": "t1st-10-4-btc-2025h2-bi-10m", "params": ("supertrend", 10, 4.0, "bi"), "asset": "BTC", "window": "10m-2025-H2"},
    {"id": "BT01.07", "rid": "t1st-14-3-btc-2024h2-bi-10m", "params": ("supertrend", 14, 3.0, "bi"), "asset": "BTC", "window": "10m-2024-H2"},
    {"id": "BT01.08", "rid": "t1st-14-3-btc-2025h1-bi-10m", "params": ("supertrend", 14, 3.0, "bi"), "asset": "BTC", "window": "10m-2025-H1"},
    {"id": "BT01.09", "rid": "t1st-14-3-btc-2025h2-bi-10m", "params": ("supertrend", 14, 3.0, "bi"), "asset": "BTC", "window": "10m-2025-H2"},
    {"id": "BT01.10", "rid": "t1ma-30-90-btc-2025h1-long-10m", "params": ("ma_crossover", 30, 90), "asset": "BTC", "window": "10m-2025-H1"},
]


# AE01 = asset expansion 1h — T3 roadmap. BB canonical + MA/ST em DOT/LINK/AVAX (novos assets).
AE01 = [
    {"id": "AE01.01", "rid": "t3bb-20-2-dot-2025h1-bi-1h", "params": ("bollinger", 20, 2.0), "asset": "DOT", "window": "2025-H1"},
    {"id": "AE01.02", "rid": "t3bb-20-2-dot-2025h2-bi-1h", "params": ("bollinger", 20, 2.0), "asset": "DOT", "window": "2025-H2"},
    {"id": "AE01.03", "rid": "t3bb-20-2-link-2025h1-bi-1h", "params": ("bollinger", 20, 2.0), "asset": "LINK", "window": "2025-H1"},
    {"id": "AE01.04", "rid": "t3bb-20-2-link-2025h2-bi-1h", "params": ("bollinger", 20, 2.0), "asset": "LINK", "window": "2025-H2"},
    {"id": "AE01.05", "rid": "t3bb-20-2-avax-2025h1-bi-1h", "params": ("bollinger", 20, 2.0), "asset": "AVAX", "window": "2025-H1"},
    {"id": "AE01.06", "rid": "t3bb-20-2-avax-2025h2-bi-1h", "params": ("bollinger", 20, 2.0), "asset": "AVAX", "window": "2025-H2"},
    {"id": "AE01.07", "rid": "t3ma-20-50-dot-2025h1-long-1h", "params": ("ma_crossover", 20, 50), "asset": "DOT", "window": "2025-H1"},
    {"id": "AE01.08", "rid": "t3ma-20-50-link-2025h1-long-1h", "params": ("ma_crossover", 20, 50), "asset": "LINK", "window": "2025-H1"},
    {"id": "AE01.09", "rid": "t3ma-20-50-avax-2025h1-long-1h", "params": ("ma_crossover", 20, 50), "asset": "AVAX", "window": "2025-H1"},
    {"id": "AE01.10", "rid": "t3st-10-3-avax-2025h1-bi-1h", "params": ("supertrend", 10, 3.0, "bi"), "asset": "AVAX", "window": "2025-H1"},
]


BATCHES = {
    "MA01": MA01,
    "MA02": MA02,
    "ST01": ST01,
    "BT01": BT01,
    "AE01": AE01,
}


def engine_args_for(entry: dict) -> list[str]:
    p = entry["params"]
    eng = p[0]
    if eng == "ma_crossover":
        short, long = p[1], p[2]
        return [
            "--strategy", eng,
            "--long-only",
            "--short-window", str(short),
            "--long-window", str(long),
        ]
    if eng == "supertrend":
        atr, mult, direction = p[1], p[2], p[3]
        args = [
            "--strategy", eng,
            "--supertrend-atr-period", str(atr),
            "--supertrend-atr-mult", str(mult),
        ]
        if direction == "long":
            args.append("--long-only")
        return args
    if eng == "bollinger":
        window, num_std = p[1], p[2]
        return [
            "--strategy", eng,
            "--bollinger-window", str(window),
            "--bollinger-num-std", str(num_std),
        ]
    raise ValueError(f"engine não reconhecida: {eng}")


def run_batch(batch_id: str) -> None:
    batch = BATCHES[batch_id]
    for entry in batch:
        ds = DATASETS[entry["asset"]][entry["window"]]
        engine = engine_args_for(entry)
        print(f"\n{'=' * 70}\n{entry['id']} | {ds} | {entry['params']}\n{'=' * 70}", flush=True)
        run(entry["rid"], ds, engine)
    print(f"\nBatch {batch_id} completo ({len(batch)} runs).", flush=True)


if __name__ == "__main__":
    bid = sys.argv[1] if len(sys.argv) > 1 else "MA01"
    run_batch(bid)
