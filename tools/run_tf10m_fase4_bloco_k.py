"""Fase 4 bloco K (supertrend) — rerun standalone sem cost_stress (OneDrive sync slowdown).

MC=500 (meia precisão vs sweep default 1000), stress omitido.
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
    "--mc-resamples", "500",
    "--mc-seed", "42",
    "--log-level", "silent",
]


def run(run_id: str, dataset: str, engine_args: list[str]) -> None:
    sys.argv = BASE_ARGS + ["--run-id", run_id, "--dataset-id", dataset] + engine_args
    cli_main()


def bloco_k() -> None:
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
            print(f"\n{'=' * 70}\n{tag} | {ds} | Supertrend 10/3.0 bi 10m (no stress)\n{'=' * 70}", flush=True)
            run(rid, ds, engine)
            i += 1


if __name__ == "__main__":
    bloco_k()
    print("\nFase 4 Bloco K completo (9 runs).", flush=True)
