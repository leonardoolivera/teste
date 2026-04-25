"""Serie CZF -- Padrao 26 regime-matched cross-window (ADR-0108).

CZE testou janelas direcionalmente opostas; 0/5 PASS = artefato de regime
(filter nao-direcional + regime oposto = FAIL estrutural, nao window-specific).

CZF testa em 2024-H1 (chop/consolidacao, regime-similar a 2025-H1).
5 runs. Gate Padrao 25 refinado: Sh >= 1.0 em janela regime-matched = replicacao.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


WIDTH_FILTER = "bollinger_width:window=30:num_std=1.5:min_width_bps=300"
TREND_SHORT = "trend_htf:htf=4h:sma_window=50:mode=short_only"

PROBES = [
    ("CZF.1", "czf-v7-eth-rsi-long-width-2024h1",
     "ethusdt_1h_20240105_20240704_binance_spot",
     "rsi", True, WIDTH_FILTER),
    ("CZF.2", "czf-v6-sol-rsi-short-trend-2024h1",
     "solusdt_1h_20240105_20240704_binance_spot",
     "rsi", False, TREND_SHORT),
    ("CZF.3", "czf-v4a-btc-rsi-short-width-2024h1",
     "btcusdt_1h_20240105_20240704_binance_spot",
     "rsi", False, WIDTH_FILTER),
    ("CZF.4", "czf-v3-btc-bollinger-short-width-2024h1",
     "btcusdt_1h_20240105_20240704_binance_spot",
     "bollinger", False, WIDTH_FILTER),
    ("CZF.5", "czf-v3-eth-bollinger-short-width-2024h1",
     "ethusdt_1h_20240105_20240704_binance_spot",
     "bollinger", False, WIDTH_FILTER),
]


def run_one(run_id: str, dataset: str, strategy: str, long_only: bool, rfilter: str) -> None:
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
        "--strategy", strategy,
        "--long-only" if long_only else "--no-long-only",
    ]
    if strategy == "rsi":
        args += ["--rsi-period", "14", "--rsi-oversold", "30", "--rsi-overbought", "70"]
    else:
        args += ["--bollinger-window", "20", "--bollinger-num-std", "1.5"]
    args += [
        "--regime-filter", rfilter,
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
    for tag, rid, ds, strat, lo, rf in PROBES:
        label = "long" if lo else "short"
        print(f"\n{'=' * 70}\n{tag} {strat}({label}) + {rf.split(':')[0]} -- {ds}\n{'=' * 70}")
        run_one(rid, ds, strat, lo, rf)
    print("\nSerie CZF completa (5 runs).")
