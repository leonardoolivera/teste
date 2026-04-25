"""Serie CZE -- Auditoria Padrao 25: rescue cross-window combos janela unica.

5 runs testando janela adicional para combos que entraram no stack ativo com
apenas 1 janela OOS validada (ADR-0107).

Tier 1 (critico):
  CZE.1: v7 ETH long+width em 2025-H1 (baseline 2024-H2)
  CZE.2: v6 SOL short+trend em 2024-H2 (baseline 2025-H1)

Tier 2 (alto):
  CZE.3: v4a BTC short+width em 2024-H2 (baseline 2025-H1)
  CZE.4: v3 BTC Bollinger short+width em 2024-H2 (baseline 2025-H1)
  CZE.5: v3 ETH Bollinger short+width em 2024-H2 (baseline 2025-H1)

Gate pre-registrado ADR-0107.
"""
from __future__ import annotations

import sys

from alpha_forge.cli.app import main as cli_main


WIDTH_FILTER = "bollinger_width:window=30:num_std=1.5:min_width_bps=300"
TREND_SHORT = "trend_htf:htf=4h:sma_window=50:mode=short_only"

PROBES = [
    # (tag, run_id, dataset, strategy, long_only, regime_filter)
    ("CZE.1", "cze-v7-eth-rsi-long-width-2025h1",
     "ethusdt_1h_20250105_20250704_binance_spot",
     "rsi", True, WIDTH_FILTER),
    ("CZE.2", "cze-v6-sol-rsi-short-trend-2024h2",
     "solusdt_1h_20240705_20241231_binance_spot",
     "rsi", False, TREND_SHORT),
    ("CZE.3", "cze-v4a-btc-rsi-short-width-2024h2",
     "btcusdt_1h_20240705_20241231_binance_spot",
     "rsi", False, WIDTH_FILTER),
    ("CZE.4", "cze-v3-btc-bollinger-short-width-2024h2",
     "btcusdt_1h_20240705_20241231_binance_spot",
     "bollinger", False, WIDTH_FILTER),
    ("CZE.5", "cze-v3-eth-bollinger-short-width-2024h2",
     "ethusdt_1h_20240705_20241231_binance_spot",
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
    print("\nSerie CZE completa (5 runs).")
