"""Audit manifest v4 (rsi_short_width_20260419) — 14 runs (ADR-0067).

Audit A: 4 combos aprovados x 2 seeds (1337, 2024) = 8 runs — lucky-MC?
Audit B: 4 combos aprovados sem regime_filter = 4 runs — atribuicao filtro.
Audit C: CH.1 (BTC 2024-H2) e CH.5 (ETH 2025-H1) com seed 1337 = 2 runs — confirma exclusao.

Seed 42 dos aprovados ja esta em results/validation/ch-rsi-*-short/ (reusa).
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


APPROVED = [
    ("CH.4", "btc", "20250105_20250704", "btcusdt_1h_20250105_20250704_binance_spot"),
    ("CH.6", "sol", "20250105_20250704", "solusdt_1h_20250105_20250704_binance_spot"),
    ("CH.7", "btc", "20250705_20251231", "btcusdt_1h_20250705_20251231_binance_spot"),
    ("CH.9", "sol", "20250705_20251231", "solusdt_1h_20250705_20251231_binance_spot"),
]

EXCLUDED_EDGE = [
    ("CH.1", "btc", "20240705_20241231", "btcusdt_1h_20240705_20241231_binance_spot"),
    ("CH.5", "eth", "20250105_20250704", "ethusdt_1h_20250105_20250704_binance_spot"),
]


def run_one(run_id: str, dataset_id: str, mc_seed: int, with_filter: bool) -> None:
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
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", str(mc_seed),
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--log-level", "silent",
    ]
    if with_filter:
        args += ["--regime-filter", "bollinger_width:window=30:num_std=1.5:min_width_bps=300"]
    spec = "width300" if with_filter else "none"
    print(f"\n{'=' * 70}\n{run_id}\n  filter={spec}  seed={mc_seed}\n{'=' * 70}")
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    # Audit A: seeds 1337 e 2024 x 4 combos aprovados = 8 runs
    for seed in (1337, 2024):
        for tag, asset, suffix, ds in APPROVED:
            rid = f"audit-v4-a-{asset}-{suffix}-seed{seed}"
            run_one(rid, ds, seed, with_filter=True)

    # Audit B: 4 combos sem filtro, seed 42
    for tag, asset, suffix, ds in APPROVED:
        rid = f"audit-v4-b-{asset}-{suffix}-nofilter"
        run_one(rid, ds, 42, with_filter=False)

    # Audit C: 2 exclusoes edge com seed 1337
    for tag, asset, suffix, ds in EXCLUDED_EDGE:
        rid = f"audit-v4-c-{asset}-{suffix}-seed1337"
        run_one(rid, ds, 1337, with_filter=True)

    print("\nManifest v4 audit completo (14 runs).")
