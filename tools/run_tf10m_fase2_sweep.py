"""Série TF10m Fase 2 — 4 engines paralelas às do stack (ADR-0197, 30 probes).

Blocos:
  B (RSI+width short, 9)
  C (BB+width long, 9)
  D (RSI+width long, 9)
  E (RSI+trend_htf short SOL, 3)
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


def bloco_b() -> None:
    """RSI+width short 10m × 9."""
    engine = [
        "--strategy", "rsi",
        "--no-long-only",
        "--rsi-period", "14",
        "--rsi-oversold", "30",
        "--rsi-overbought", "70",
        "--regime-filter", "bollinger_width:window=30:num_std=1.5:min_width_bps=250",
    ]
    i = 1
    for w in WINDOWS_ORDER:
        for a in ASSETS_ORDER:
            ds = DATASETS[a][w]
            rid = f"tf10b-rsi-30-70-width-{a}-{w}-short-10m"
            tag = f"TF10B.{i}"
            print(f"\n{'=' * 70}\n{tag} | {ds} | RSI 30/70 short + width 10m\n{'=' * 70}")
            run(rid, ds, engine)
            i += 1


def bloco_c() -> None:
    """BB+width long 10m × 9. BB window=30, ns=1.5 (canonical long stack)."""
    engine = [
        "--strategy", "bollinger",
        "--long-only",
        "--bollinger-window", "30",
        "--bollinger-num-std", "1.5",
        "--regime-filter", "bollinger_width:window=30:num_std=1.5:min_width_bps=250",
    ]
    i = 1
    for w in WINDOWS_ORDER:
        for a in ASSETS_ORDER:
            ds = DATASETS[a][w]
            rid = f"tf10c-bol-30-15-width-{a}-{w}-long-10m"
            tag = f"TF10C.{i}"
            print(f"\n{'=' * 70}\n{tag} | {ds} | BB 30/1.5 long + width 10m\n{'=' * 70}")
            run(rid, ds, engine)
            i += 1


def bloco_d() -> None:
    """RSI+width long 10m × 9."""
    engine = [
        "--strategy", "rsi",
        "--long-only",
        "--rsi-period", "14",
        "--rsi-oversold", "30",
        "--rsi-overbought", "70",
        "--regime-filter", "bollinger_width:window=30:num_std=1.5:min_width_bps=250",
    ]
    i = 1
    for w in WINDOWS_ORDER:
        for a in ASSETS_ORDER:
            ds = DATASETS[a][w]
            rid = f"tf10d-rsi-30-70-width-{a}-{w}-long-10m"
            tag = f"TF10D.{i}"
            print(f"\n{'=' * 70}\n{tag} | {ds} | RSI 30/70 long + width 10m\n{'=' * 70}")
            run(rid, ds, engine)
            i += 1


def bloco_e() -> None:
    """RSI+trend_htf short SOL 10m × 3 (SOL only, stack canonical 25/75)."""
    engine = [
        "--strategy", "rsi",
        "--no-long-only",
        "--rsi-period", "14",
        "--rsi-oversold", "25",
        "--rsi-overbought", "75",
        "--regime-filter", "trend_htf:htf=4h:sma_window=50:mode=short_only",
    ]
    i = 1
    for w in WINDOWS_ORDER:
        ds = DATASETS["sol"][w]
        rid = f"tf10e-rsi-25-75-trendhtf-sol-{w}-short-10m"
        tag = f"TF10E.{i}"
        print(f"\n{'=' * 70}\n{tag} | {ds} | RSI 25/75 short + trend_htf SOL 10m\n{'=' * 70}")
        run(rid, ds, engine)
        i += 1


if __name__ == "__main__":
    bloco_b()
    bloco_c()
    bloco_d()
    bloco_e()
    print("\nSérie TF10m Fase 2 completa (30 runs).")
