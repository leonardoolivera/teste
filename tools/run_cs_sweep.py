"""Serie CS -- replicacao opt-in v2 long grandfather (ADR-0111 followup).

Testa BTC 2024-H2 e SOL 2024-H2 (v2 long, bollinger 30/1.5 + width250) em 2
janelas adicionais cada pra upgrade grandfather -> contextual/strict.

Engine v2 long: long_only=true, window=30, num_std=1.5, min_width_bps=250.
Gate contextual: Sh >= 0.5 em >=1 janela adicional regime-matched.
Gate strict: Sh >= 1.0 em >=1 janela adicional.

4 runs: BTC/SOL x 2024-H1/2025-H1.
Note: 2024-H1 = chop/consolidacao pre-bull. 2025-H1 = chop. Ambas regime-matched.
2024-H2 baseline e bull-com-chop; alternativas devem ser menos bull-heavy.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


WIDTH_FILTER = "bollinger_width:window=30:num_std=1.5:min_width_bps=250"

PROBES = [
    ("CS.1", "cs-v2-btc-long-bol-width250-2024h1",
     "btcusdt_1h_20240105_20240704_binance_spot"),
    ("CS.2", "cs-v2-btc-long-bol-width250-2025h1",
     "btcusdt_1h_20250105_20250704_binance_spot"),
    ("CS.3", "cs-v2-sol-long-bol-width250-2024h1",
     "solusdt_1h_20240105_20240704_binance_spot"),
    ("CS.4", "cs-v2-sol-long-bol-width250-2025h1",
     "solusdt_1h_20250105_20250704_binance_spot"),
]


def run_one(run_id: str, dataset: str) -> None:
    args = [
        "alpha-forge", "validate",
        "--run-id", run_id,
        "--dataset-id", dataset,
        "--capital", "10000.0",
        "--fracao", "0.1",
        "--alavancagem", "2.0",
        "--sizing-mode", "fixed_notional",
        "--taker-fee-bps", "5.0",
        "--slippage-bps-per-notional", "2.0",
        "--spread-bps", "0.0",
        "--strategy", "bollinger",
        "--long-only",
        "--bollinger-window", "30",
        "--bollinger-num-std", "1.5",
        "--regime-filter", WIDTH_FILTER,
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--log-level", "info",
    ]
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, rid, ds in PROBES:
        print(f"\n{'=' * 70}\n{tag} bollinger(long) width250 -- {ds}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CS completa (4 runs).")
