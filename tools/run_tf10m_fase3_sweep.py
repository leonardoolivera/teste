"""Série TF10m Fase 3 — outras MR strategies (ADR-0199, 27 probes).

Blocos:
  F (zscore, 9)
  G (keltner, 9)
  H (composite_bb_rsi, 9)
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


def bloco_f() -> None:
    """zscore MR 10m × 9."""
    engine = [
        "--strategy", "zscore",
        "--no-long-only",
        "--zscore-window", "20",
        "--zscore-threshold", "2.0",
    ]
    i = 1
    for w in WINDOWS_ORDER:
        for a in ASSETS_ORDER:
            ds = DATASETS[a][w]
            rid = f"tf10f-zscore-20-2-{a}-{w}-10m"
            tag = f"TF10F.{i}"
            print(f"\n{'=' * 70}\n{tag} | {ds} | zscore 20/2.0 10m\n{'=' * 70}")
            run(rid, ds, engine)
            i += 1


def bloco_g() -> None:
    """Keltner MR 10m × 9."""
    engine = [
        "--strategy", "keltner",
        "--no-long-only",
        "--keltner-window", "20",
        "--keltner-atr-period", "14",
        "--keltner-mult", "2.0",
    ]
    i = 1
    for w in WINDOWS_ORDER:
        for a in ASSETS_ORDER:
            ds = DATASETS[a][w]
            rid = f"tf10g-keltner-20-14-2-{a}-{w}-10m"
            tag = f"TF10G.{i}"
            print(f"\n{'=' * 70}\n{tag} | {ds} | Keltner 20/14/2.0 10m\n{'=' * 70}")
            run(rid, ds, engine)
            i += 1


def bloco_h() -> None:
    """composite_bb_rsi 10m × 9."""
    engine = [
        "--strategy", "composite_bb_rsi",
        "--no-long-only",
        "--composite-bb-window", "20",
        "--composite-bb-num-std", "2.0",
        "--composite-rsi-period", "14",
        "--composite-rsi-oversold", "30",
        "--composite-rsi-overbought", "70",
    ]
    i = 1
    for w in WINDOWS_ORDER:
        for a in ASSETS_ORDER:
            ds = DATASETS[a][w]
            rid = f"tf10h-composite-20-2-14-30-70-{a}-{w}-10m"
            tag = f"TF10H.{i}"
            print(f"\n{'=' * 70}\n{tag} | {ds} | composite BB 20/2 + RSI 30/70 10m\n{'=' * 70}")
            run(rid, ds, engine)
            i += 1


if __name__ == "__main__":
    bloco_f()
    bloco_g()
    bloco_h()
    print("\nSérie TF10m Fase 3 completa (27 runs).")
