"""Serie CR -- TrendHTF cross-asset BTC/ETH 2025-H1 (4 runs).

Gate pre-registrado em ADR-0085. Testa se trend-only generaliza para BTC+ETH
no regime chop 2025-H1 (v6 SOL ja ativo). Gate B naked incluido (Padrao 19).
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


PILOTS = [
    ("CR.1-trend", "btcusdt_1h_20250105_20250704_binance_spot", "20250105_20250704",
     "trend_htf:htf=4h:sma_window=50:mode=short_only", "cr-btc-trend"),
    ("CR.1-naked", "btcusdt_1h_20250105_20250704_binance_spot", "20250105_20250704",
     None, "cr-btc-naked"),
    ("CR.2-trend", "ethusdt_1h_20250105_20250704_binance_spot", "20250105_20250704",
     "trend_htf:htf=4h:sma_window=50:mode=short_only", "cr-eth-trend"),
    ("CR.2-naked", "ethusdt_1h_20250105_20250704_binance_spot", "20250105_20250704",
     None, "cr-eth-naked"),
]


def run_one(run_id: str, dataset_id: str, regime_filter: str | None) -> None:
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
        "--mc-seed", "42",
        "--stress", "fee+10:10:0:0",
        "--stress", "spread+10:0:0:10",
        "--log-level", "silent",
    ]
    if regime_filter is not None:
        args.extend(["--regime-filter", regime_filter])
    sys.argv = args
    cli_main()


if __name__ == "__main__":
    for tag, ds, suffix, filt, prefix in PILOTS:
        rid = f"{prefix}-{suffix}-short"
        filter_desc = filt if filt else "NAKED (no filter)"
        print(f"\n{'=' * 70}\n{tag} RSI short + {filter_desc} -- {ds}\n{'=' * 70}")
        run_one(rid, ds, filt)
    print("\nSerie CR completa (4 runs).")
