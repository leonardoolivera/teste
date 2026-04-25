"""Serie DC -- baseline screening alts (DOT/AVAX/LINK) 2025-H1 (ADR-0162 Fase A).

3 engines x 3 assets = 9 runs:
- bol short + width
- rsi short + width
- rsi short + trend_htf
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


WIDTH_FILTER = "bollinger_width:window=30:num_std=1.5:min_width_bps=300"
TREND_FILTER = "trend_htf:htf=4h:sma_window=50:mode=short_only"

ASSETS = [
    ("DOT", "dotusdt_1h_20250105_20250704_binance_spot"),
    ("AVAX", "avaxusdt_1h_20250105_20250704_binance_spot"),
    ("LINK", "linkusdt_1h_20250105_20250704_binance_spot"),
]


def bol_args(run_id: str, dataset: str, regime: str) -> list[str]:
    return [
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
        "--no-long-only",
        "--bollinger-window", "20",
        "--bollinger-num-std", "1.5",
        "--n-folds", "5",
        "--scheme", "rolling",
        "--train-fraction", "0.5",
        "--min-test-bars", "50",
        "--mc-resamples", "1000",
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--regime-filter", regime,
        "--log-level", "info",
    ]


def rsi_args(run_id: str, dataset: str, regime: str) -> list[str]:
    return [
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
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--regime-filter", regime,
        "--log-level", "info",
    ]


def main() -> None:
    probes = []
    for label, ds in ASSETS:
        probes.append((f"DC.{label}.1", f"dc-{label.lower()}-bol-20-15-width-short-1h-2025h1", ds, "bol", WIDTH_FILTER))
        probes.append((f"DC.{label}.2", f"dc-{label.lower()}-rsi-30-70-width-short-1h-2025h1", ds, "rsi", WIDTH_FILTER))
        probes.append((f"DC.{label}.3", f"dc-{label.lower()}-rsi-30-70-trendhtf-short-1h-2025h1", ds, "rsi", TREND_FILTER))

    for tag, rid, ds, engine, rgf in probes:
        print(f"\n{'=' * 70}\n{tag} | {engine} | {ds}\nfilter={rgf}\n{'=' * 70}")
        sys.argv = bol_args(rid, ds, rgf) if engine == "bol" else rsi_args(rid, ds, rgf)
        cli_main()
    print("\nSerie DC completa (9 runs).")


if __name__ == "__main__":
    main()
