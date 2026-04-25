"""Audit do manifest bollinger_width_regime_20260418_v2 — 5 runs.

Audit A — SOL 2024-H2 sob 3 seeds alternativos (42, 1337, 2024) — lucky-MC?
Audit B — SOL 2024-H2 sem regime_filter — atribuicao do filtro.
Audit C — SOL 2025-H1 com engine exata do manifest — confirma exclusao.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


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
        "--long-only",
        "--bollinger-window", "30",
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
        args += ["--regime-filter", "bollinger_width:window=30:num_std=1.5:min_width_bps=250"]
    spec = "bollinger_width:window=30:num_std=1.5:min_width_bps=250" if with_filter else "none"
    print(f"\n{'=' * 70}\n{run_id}\n  filter={spec}  seed={mc_seed}\n{'=' * 70}")
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    sol24h2 = "solusdt_1h_20240705_20241231_binance_spot"
    sol25h1 = "solusdt_1h_20250105_20250704_binance_spot"

    # Audit A: 3 seeds no SOL 2024-H2 com manifest completo
    for seed in (42, 1337, 2024):
        run_one(f"audit-a-sol-2024h2-seed{seed}", sol24h2, seed, with_filter=True)

    # Audit B: SOL 2024-H2 sem filtro (Bollinger puro)
    run_one("audit-b-sol-2024h2-nofilter", sol24h2, 42, with_filter=False)

    # Audit C: SOL 2025-H1 com engine exata do manifest
    run_one("audit-c-sol-2025h1-manifest", sol25h1, 42, with_filter=True)

    print("\nManifest audit completo (5 runs).")
