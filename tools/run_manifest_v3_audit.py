"""Audit manifest v3 (bollinger_short_width_20260419) — 14 runs.

Audit A: 4 combos aprovados x 3 seeds (42, 1337, 2024) = 12 runs — lucky-MC?
Audit B: 4 combos aprovados sem regime_filter = 4 runs — atribuicao filtro.
Audit C: CG.1 (BTC 2024-H2) e CG.9 (SOL 2025-H2) com seed 1337 = 2 runs — confirma exclusao.

Ja temos Audit A seed=42 em results/validation/cg-bol-* (da Serie CG). Reutilizamos.
Novas runs: 8 (A seeds 1337+2024) + 4 (B) + 2 (C) = 14 runs.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


APPROVED = [
    ("CG.3", "sol", "20240705_20241231", "solusdt_1h_20240705_20241231_binance_spot"),
    ("CG.4", "btc", "20250105_20250704", "btcusdt_1h_20250105_20250704_binance_spot"),
    ("CG.5", "eth", "20250105_20250704", "ethusdt_1h_20250105_20250704_binance_spot"),
    ("CG.6", "sol", "20250105_20250704", "solusdt_1h_20250105_20250704_binance_spot"),
]

EXCLUDED_SEVERE = [
    ("CG.1", "btc", "20240705_20241231", "btcusdt_1h_20240705_20241231_binance_spot"),
    ("CG.9", "sol", "20250705_20251231", "solusdt_1h_20250705_20251231_binance_spot"),
]


def run_one(run_id: str, dataset_id: str, mc_seed: int, with_filter: bool) -> None:
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
    # (seed 42 ja existe em cg-bol-*, reutilizado na summarizer)
    for seed in (1337, 2024):
        for tag, asset, suffix, ds in APPROVED:
            rid = f"audit-v3-a-{asset}-{suffix}-seed{seed}"
            run_one(rid, ds, seed, with_filter=True)

    # Audit B: 4 combos sem filtro, seed 42
    for tag, asset, suffix, ds in APPROVED:
        rid = f"audit-v3-b-{asset}-{suffix}-nofilter"
        run_one(rid, ds, 42, with_filter=False)

    # Audit C: 2 exclusoes severas com seed 1337
    for tag, asset, suffix, ds in EXCLUDED_SEVERE:
        rid = f"audit-v3-c-{asset}-{suffix}-seed1337"
        run_one(rid, ds, 1337, with_filter=True)

    print("\nManifest v3 audit completo (14 runs).")
