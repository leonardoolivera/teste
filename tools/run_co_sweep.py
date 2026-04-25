"""Serie CO -- RSI(14/30/70) short + composicao AND width 300 + TrendHTF SOL-only (3 runs).

Gate pre-registrado em ADR-0078. Testa se composicao eleva edge alem das pernas isoladas.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CO.1", "solusdt_1h_20240705_20241231_binance_spot", "20240705_20241231"),
    ("CO.2", "solusdt_1h_20250105_20250704_binance_spot", "20250105_20250704"),
    ("CO.3", "solusdt_1h_20250705_20251231_binance_spot", "20250705_20251231"),
]

FILTER_SPEC = (
    "and("
    "bollinger_width:window=30:num_std=1.5:min_width_bps=300,"
    "trend_htf:htf=4h:sma_window=50:mode=short_only"
    ")"
)


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
        "--regime-filter", FILTER_SPEC,
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
    for tag, ds, suffix in PILOTS:
        rid = f"co-rsi-width300-trendhtf-sol-{suffix}-short"
        print(f"\n{'=' * 70}\n{tag} RSI short + and(width300, trendHTF) -- SOL {suffix}\n{'=' * 70}")
        run_one(rid, ds)
    print("\nSerie CO completa (3 runs).")
