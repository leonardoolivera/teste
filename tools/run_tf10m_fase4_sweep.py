"""Série TF10m Fase 4 — non-MR strategies (ADR-0201, 27 probes).

Blocos:
  I (ma_crossover, 9)
  J (donchian, 9)
  K (supertrend, 9)
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


DATASETS = {
    "btc": {
        "2024h2": "btcusdt_10m_20240705_20241231_binance_spot_resampled",
        "2025h1": "btcusdt_10m_20250105_20250704_binance_spot_resampled",
        "2025h2": "btcusdt_10m_20250705_20251231_binance_spot_resampled",
    },
    "eth": {
        "2024h2": "ethusdt_10m_20240705_20241231_binance_spot_resampled",
        "2025h1": "ethusdt_10m_20250105_20250704_binance_spot_resampled",
        "2025h2": "ethusdt_10m_20250705_20251231_binance_spot_resampled",
    },
    "sol": {
        "2024h2": "solusdt_10m_20240705_20241231_binance_spot_resampled",
        "2025h1": "solusdt_10m_20250105_20250704_binance_spot_resampled",
        "2025h2": "solusdt_10m_20250705_20251231_binance_spot_resampled",
    },
}

WINDOWS_ORDER = ["2024h2", "2025h1", "2025h2"]
ASSETS_ORDER = ["btc", "eth", "sol"]


BASE_ARGS = [
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
    "--mc-resamples", "1000",
    "--mc-seed", "42",
    "--stress", "fee+10:10:0:0",
    "--stress", "spread+10:0:0:10",
    "--log-level", "silent",
]


def run(run_id: str, dataset: str, engine_args: list[str]) -> None:
    sys.argv = BASE_ARGS + ["--run-id", run_id, "--dataset-id", dataset] + engine_args
    cli_main()


def bloco_i() -> None:
    """ma_crossover 20/50 long 10m × 9."""
    engine = [
        "--strategy", "ma_crossover",
        "--long-only",
        "--short-window", "20",
        "--long-window", "50",
    ]
    i = 1
    for w in WINDOWS_ORDER:
        for a in ASSETS_ORDER:
            ds = DATASETS[a][w]
            rid = f"tf10i-macx-20-50-{a}-{w}-long-10m"
            tag = f"TF10I.{i}"
            print(f"\n{'=' * 70}\n{tag} | {ds} | MAcx 20/50 long 10m\n{'=' * 70}")
            run(rid, ds, engine)
            i += 1


def bloco_j() -> None:
    """donchian 20/10 long 10m × 9."""
    engine = [
        "--strategy", "donchian",
        "--long-only",
        "--entry-window", "20",
        "--exit-window", "10",
    ]
    i = 1
    for w in WINDOWS_ORDER:
        for a in ASSETS_ORDER:
            ds = DATASETS[a][w]
            rid = f"tf10j-donch-20-10-{a}-{w}-long-10m"
            tag = f"TF10J.{i}"
            print(f"\n{'=' * 70}\n{tag} | {ds} | Donchian 20/10 long 10m\n{'=' * 70}")
            run(rid, ds, engine)
            i += 1


def bloco_k() -> None:
    """supertrend atr=10 mult=3.0 bi 10m × 9."""
    engine = [
        "--strategy", "supertrend",
        "--no-long-only",
        "--supertrend-atr-period", "10",
        "--supertrend-atr-mult", "3.0",
    ]
    i = 1
    for w in WINDOWS_ORDER:
        for a in ASSETS_ORDER:
            ds = DATASETS[a][w]
            rid = f"tf10k-st-10-3-{a}-{w}-bi-10m"
            tag = f"TF10K.{i}"
            print(f"\n{'=' * 70}\n{tag} | {ds} | Supertrend 10/3.0 bi 10m\n{'=' * 70}")
            run(rid, ds, engine)
            i += 1


if __name__ == "__main__":
    bloco_i()
    bloco_j()
    bloco_k()
    print("\nSérie TF10m Fase 4 completa (27 runs).")
