"""Re-teste diagnóstico do stack 13 com cada entrada = 100% do capital corrente.

ADR-0204 (pré-reg diagnóstico). ADR-0205 (closeout).

Sizing:
  - SNOWBALL 100%: RiskBudget(fracao=1.0, alav=1.0, sizing_mode=SNOWBALL) ->
    cada ENTER usa capital_corrente = capital_inicial + realized_pnl.
  - Baseline comparação: fracao=0.1, alav=2.0, sizing_mode=FIXED_NOTIONAL
    (match notional_per_trade_quote_ccy=2000 dos manifests).

Cost model baseline (match manifests cost_model_baseline_pct ~0.14):
  taker_fee_bps=5, slippage_bps_per_unit_notional=2, spread_bps=0.

Saída: exports/diag/snowball_100_stack13_<date>.json.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.data.loaders import load_dataset
from alpha_forge.regimes.filter import (
    BollingerWidthFilter,
    TrendHTFRegimeFilter,
)
from alpha_forge.risk.schemas import RiskBudget, SizingMode
from alpha_forge.strategies.families.bollinger import BollingerMeanReversionStrategy
from alpha_forge.strategies.families.rsi import RSIMeanReversionStrategy


CAPITAL = 10_000.0
BARS_PER_YEAR_1H = 24 * 365

# Cost match manifest baseline 14 bps round-trip.
COST = CostModel(
    taker_fee_bps=5.0,
    slippage_bps_per_unit_notional=2.0,
    spread_bps=0.0,
)

# ------------------------------------------------------------------------------
# 13 combos (lido manualmente dos manifests ativos em exports/approved/).
# ------------------------------------------------------------------------------

COMBOS: list[dict] = [
    # --- Manifest: bollinger_width_regime_20260418_v2.json (BB long+width) ---
    dict(
        manifest="bollinger_width_regime_v2",
        symbol="ETHUSDT", window_tag="2024-H1",
        dataset_id="ethusdt_1h_20240105_20240704_binance_spot",
        baseline_sharpe=1.834, baseline_pnl_pct=4.678, baseline_trades=38,
        strategy_kind="bollinger", long_only=True,
        strat_params=dict(window=30, num_std=1.5),
        regime=("bb_width", dict(window=30, num_std=1.5, min_width_bps=250)),
    ),
    dict(
        manifest="bollinger_width_regime_v2",
        symbol="ETHUSDT", window_tag="2025-H1",
        dataset_id="ethusdt_1h_20250105_20250704_binance_spot",
        baseline_sharpe=1.21, baseline_pnl_pct=3.71, baseline_trades=36,
        strategy_kind="bollinger", long_only=True,
        strat_params=dict(window=30, num_std=1.5),
        regime=("bb_width", dict(window=30, num_std=1.5, min_width_bps=250)),
    ),
    dict(
        manifest="bollinger_width_regime_v2",
        symbol="BTCUSDT", window_tag="2024-H2",
        dataset_id="btcusdt_1h_20240705_20241231_binance_spot",
        baseline_sharpe=1.559, baseline_pnl_pct=2.24, baseline_trades=30,
        strategy_kind="bollinger", long_only=True,
        strat_params=dict(window=30, num_std=1.5),
        regime=("bb_width", dict(window=30, num_std=1.5, min_width_bps=250)),
    ),
    dict(
        manifest="bollinger_width_regime_v2",
        symbol="SOLUSDT", window_tag="2024-H2",
        dataset_id="solusdt_1h_20240705_20241231_binance_spot",
        baseline_sharpe=2.401, baseline_pnl_pct=8.011, baseline_trades=69,
        strategy_kind="bollinger", long_only=True,
        strat_params=dict(window=30, num_std=1.5),
        regime=("bb_width", dict(window=30, num_std=1.5, min_width_bps=250)),
    ),
    # --- Manifest: bollinger_short_width_20260419.json (BB bi-directional, width 300) ---
    dict(
        manifest="bollinger_short_width",
        symbol="SOLUSDT", window_tag="2024-H2",
        dataset_id="solusdt_1h_20240705_20241231_binance_spot",
        baseline_sharpe=1.38, baseline_pnl_pct=6.637, baseline_trades=102,
        strategy_kind="bollinger", long_only=False,
        strat_params=dict(window=20, num_std=1.5),
        regime=("bb_width", dict(window=30, num_std=1.5, min_width_bps=300)),
    ),
    dict(
        manifest="bollinger_short_width",
        symbol="BTCUSDT", window_tag="2025-H1",
        dataset_id="btcusdt_1h_20250105_20250704_binance_spot",
        baseline_sharpe=1.243, baseline_pnl_pct=2.961, baseline_trades=37,
        strategy_kind="bollinger", long_only=False,
        strat_params=dict(window=20, num_std=1.5),
        regime=("bb_width", dict(window=30, num_std=1.5, min_width_bps=300)),
    ),
    dict(
        manifest="bollinger_short_width",
        symbol="ETHUSDT", window_tag="2025-H1",
        dataset_id="ethusdt_1h_20250105_20250704_binance_spot",
        baseline_sharpe=2.395, baseline_pnl_pct=12.156, baseline_trades=85,
        strategy_kind="bollinger", long_only=False,
        strat_params=dict(window=20, num_std=1.5),
        regime=("bb_width", dict(window=30, num_std=1.5, min_width_bps=300)),
    ),
    dict(
        manifest="bollinger_short_width",
        symbol="SOLUSDT", window_tag="2025-H1",
        dataset_id="solusdt_1h_20250105_20250704_binance_spot",
        baseline_sharpe=2.713, baseline_pnl_pct=17.474, baseline_trades=109,
        strategy_kind="bollinger", long_only=False,
        strat_params=dict(window=20, num_std=1.5),
        regime=("bb_width", dict(window=30, num_std=1.5, min_width_bps=300)),
    ),
    # --- Manifest: rsi_long_width_eth_2024h2_20260420.json ---
    dict(
        manifest="rsi_long_width_eth_2024h2",
        symbol="ETHUSDT", window_tag="2024-H2",
        dataset_id="ethusdt_1h_20240705_20241231_binance_spot",
        baseline_sharpe=1.774, baseline_pnl_pct=3.09, baseline_trades=30,
        strategy_kind="rsi", long_only=True,
        strat_params=dict(period=14, oversold=30, overbought=70),
        regime=("bb_width", dict(window=30, num_std=1.5, min_width_bps=300)),
    ),
    # --- Manifest: rsi_short_pure_2025h2_20260420b.json (no regime filter) ---
    dict(
        manifest="rsi_short_pure_2025h2",
        symbol="BTCUSDT", window_tag="2025-H2",
        dataset_id="btcusdt_1h_20250705_20251231_binance_spot",
        baseline_sharpe=1.64, baseline_pnl_pct=5.126, baseline_trades=92,
        strategy_kind="rsi", long_only=False,
        strat_params=dict(period=14, oversold=30, overbought=70),
        regime=None,
    ),
    dict(
        manifest="rsi_short_pure_2025h2",
        symbol="SOLUSDT", window_tag="2025-H2",
        dataset_id="solusdt_1h_20250705_20251231_binance_spot",
        baseline_sharpe=2.3, baseline_pnl_pct=13.812, baseline_trades=86,
        strategy_kind="rsi", long_only=False,
        strat_params=dict(period=14, oversold=30, overbought=70),
        regime=None,
    ),
    # --- Manifest: rsi_short_trendhtf_2025h1_sol_20260420.json ---
    dict(
        manifest="rsi_short_trendhtf_sol_2025h1",
        symbol="SOLUSDT", window_tag="2025-H1",
        dataset_id="solusdt_1h_20250105_20250704_binance_spot",
        baseline_sharpe=2.0, baseline_pnl_pct=9.8, baseline_trades=32,
        strategy_kind="rsi", long_only=False,
        strat_params=dict(period=14, oversold=25, overbought=75),
        regime=("trend_htf", dict(htf="4h", sma_window=50, mode="short_only")),
    ),
    # --- Manifest: rsi_short_width_2025h1_20260419.json (retém só BTC 2025-H1) ---
    dict(
        manifest="rsi_short_width_2025h1",
        symbol="BTCUSDT", window_tag="2025-H1",
        dataset_id="btcusdt_1h_20250105_20250704_binance_spot",
        baseline_sharpe=1.688, baseline_pnl_pct=4.066, baseline_trades=37,
        strategy_kind="rsi", long_only=False,
        strat_params=dict(period=14, oversold=30, overbought=70),
        regime=("bb_width", dict(window=30, num_std=1.5, min_width_bps=300)),
    ),
]


def build_strategy(combo: dict):
    kind = combo["strategy_kind"]
    p = combo["strat_params"]
    long_only = combo["long_only"]
    if kind == "bollinger":
        return BollingerMeanReversionStrategy(
            window=p["window"], num_std=p["num_std"], long_only=long_only
        )
    if kind == "rsi":
        return RSIMeanReversionStrategy(
            period=p["period"],
            oversold=p["oversold"],
            overbought=p["overbought"],
            long_only=long_only,
        )
    raise ValueError(f"strategy_kind desconhecida: {kind}")


def build_regime_filter(combo: dict):
    spec = combo["regime"]
    if spec is None:
        return None
    name, kwargs = spec
    if name == "bb_width":
        return BollingerWidthFilter(**kwargs)
    if name == "trend_htf":
        return TrendHTFRegimeFilter(**kwargs)
    raise ValueError(f"regime desconhecido: {name}")


def annualized_sharpe_bar_returns(
    equity: list[float], bars_per_year: int = BARS_PER_YEAR_1H
) -> float | None:
    """Sharpe annualized a partir da equity curve por barra (rf=0)."""
    if len(equity) < 3:
        return None
    # pct returns por barra; proteção contra equity ≤ 0.
    rets: list[float] = []
    for i in range(1, len(equity)):
        prev = equity[i - 1]
        cur = equity[i]
        if prev <= 0.0:
            rets.append(0.0)
        else:
            rets.append((cur - prev) / prev)
    if not rets:
        return None
    n = len(rets)
    mean = sum(rets) / n
    var = sum((r - mean) ** 2 for r in rets) / (n - 1 if n > 1 else 1)
    sd = math.sqrt(var)
    if sd <= 0:
        return None
    return (mean / sd) * math.sqrt(bars_per_year)


def run_one(combo: dict, *, sizing: str) -> dict:
    if sizing == "fixed_100":
        # 100% do capital_inicial por entrada, sem compounding (fixed notional).
        budget = RiskBudget(
            capital_inicial=CAPITAL,
            fracao_por_trade=1.0,
            alavancagem_max=1.0,
            sizing_mode=SizingMode.FIXED_NOTIONAL,
        )
    elif sizing == "baseline_fixed_20pct":
        # Match manifest notional_per_trade_quote_ccy=2000 on capital 10k.
        budget = RiskBudget(
            capital_inicial=CAPITAL,
            fracao_por_trade=0.1,
            alavancagem_max=2.0,
            sizing_mode=SizingMode.FIXED_NOTIONAL,
        )
    else:
        raise ValueError(sizing)

    prices = load_dataset(combo["dataset_id"])
    strategy = build_strategy(combo)
    regime_filter = build_regime_filter(combo)
    result = run_backtest(
        prices=prices,
        strategy=strategy,
        budget=budget,
        cost_model=COST,
        dataset_id=combo["dataset_id"],
        regime_filter=regime_filter,
    )
    m = result.metrics
    equity_vals = [v for _, v in result.equity_curve]
    sharpe = annualized_sharpe_bar_returns(equity_vals)
    pnl_pct = (result.final_equity / CAPITAL - 1.0) * 100.0
    min_eq = min(equity_vals) if equity_vals else CAPITAL
    max_eq = max(equity_vals) if equity_vals else CAPITAL
    sizing_rejections = sum(
        1 for r in result.rejections if "size" in r.reason.value.lower()
    )
    blow_up = min_eq <= 0.0
    return dict(
        sizing=sizing,
        final_equity=round(result.final_equity, 2),
        pnl_pct=round(pnl_pct, 3),
        max_equity=round(max_eq, 2),
        min_equity=round(min_eq, 2),
        max_drawdown_pct=round((m.max_drawdown if m else 0.0) * 100.0, 3),
        trade_count=m.trade_count if m else 0,
        hit_rate_pct=(
            round(m.hit_rate * 100.0, 2) if (m and m.hit_rate is not None) else None
        ),
        sharpe_annual=round(sharpe, 3) if sharpe is not None else None,
        sizing_rejections=sizing_rejections,
        blow_up=blow_up,
    )


def main() -> int:
    out: list[dict] = []
    for i, combo in enumerate(COMBOS, 1):
        label = f"{combo['manifest']}/{combo['symbol']}/{combo['window_tag']}"
        print(f"[{i:02d}/{len(COMBOS)}] {label} ...", flush=True)
        try:
            fixed_100 = run_one(combo, sizing="fixed_100")
            baseline = run_one(combo, sizing="baseline_fixed_20pct")
        except Exception as exc:  # noqa: BLE001
            print(f"    FAIL: {exc}", flush=True)
            out.append(dict(combo=label, error=str(exc)))
            continue
        row = dict(
            manifest=combo["manifest"],
            symbol=combo["symbol"],
            window_tag=combo["window_tag"],
            dataset_id=combo["dataset_id"],
            strategy_kind=combo["strategy_kind"],
            long_only=combo["long_only"],
            regime=combo["regime"],
            baseline_manifest=dict(
                sharpe=combo["baseline_sharpe"],
                pnl_pct=combo["baseline_pnl_pct"],
                trades=combo["baseline_trades"],
            ),
            baseline_fullperiod=baseline,
            fixed_100=fixed_100,
        )
        print(
            f"    baseline20%: Sh={baseline['sharpe_annual']} "
            f"PnL%={baseline['pnl_pct']} tr={baseline['trade_count']} "
            f"| fixed100%: Sh={fixed_100['sharpe_annual']} "
            f"PnL%={fixed_100['pnl_pct']} tr={fixed_100['trade_count']} "
            f"MDD={fixed_100['max_drawdown_pct']}% "
            f"min_eq={fixed_100['min_equity']} blow={fixed_100['blow_up']}",
            flush=True,
        )
        out.append(row)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    payload = dict(
        adr_prereg="decisions/0204-snowball-100pct-per-entry-stack13-prereg.md",
        capital_inicial=CAPITAL,
        cost_model=dict(
            taker_fee_bps=COST.taker_fee_bps,
            slippage_bps_per_unit_notional=COST.slippage_bps_per_unit_notional,
            spread_bps=COST.spread_bps,
        ),
        bars_per_year=BARS_PER_YEAR_1H,
        sizing_configs=dict(
            baseline_fixed_20pct=dict(
                fracao=0.1, alav=2.0, mode="fixed_notional",
                effective_notional_per_trade_usd=2000,
            ),
            fixed_100=dict(
                fracao=1.0, alav=1.0, mode="fixed_notional",
                effective_notional_per_trade_usd=10_000,
                note="100% do capital_inicial por entrada; sem snowball (sem compounding).",
            ),
        ),
        generated_at=datetime.now(timezone.utc).isoformat(),
        combos=out,
    )
    out_path = Path(f"exports/diag/fixed_100_stack13_{stamp}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nwrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
