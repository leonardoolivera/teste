"""Integration: `walk_forward` + `monte_carlo_trades` end-to-end (ADR-0003).

Valida que walk-forward causal sobre MA 20/50 no dataset sintético produz
folds com shape esperado, e que Monte Carlo sobre trades agregados retorna
summary com percentis bem ordenados. Não avalia edge; valida pipeline.
"""

from __future__ import annotations

import pandas as pd
import pytest

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.schemas import (
    BacktestMetrics,
    BacktestResult,
    Side,
    Trade,
)
from alpha_forge.data.loaders import DatasetNotFoundError, load_dataset
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.ma_crossover import (
    MovingAverageCrossoverStrategy,
)
from alpha_forge.validation import (
    MonteCarloSummary,
    monte_carlo_trades,
    walk_forward,
)

REFERENCE_DATASET_ID = "synthetic_btcusdt_1h_seed42"


@pytest.fixture(scope="module")
def prices() -> pd.DataFrame:
    try:
        return load_dataset(REFERENCE_DATASET_ID)
    except (DatasetNotFoundError, FileNotFoundError) as exc:
        pytest.skip(f"dataset seminal ausente: {exc}")


def test_walk_forward_plus_monte_carlo(prices: pd.DataFrame) -> None:
    folds = walk_forward(
        prices=prices,
        strategy=MovingAverageCrossoverStrategy(short_window=20, long_window=50),
        budget=RiskBudget(
            capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0
        ),
        cost_model=CostModel(taker_fee_bps=5.0, slippage_bps_per_unit_notional=2.0),
        dataset_id=REFERENCE_DATASET_ID,
        n_folds=5,
        scheme="rolling",
        train_fraction=0.5,
        min_test_bars=50,
    )
    assert len(folds) >= 1
    total_test_bars = sum(f.test_window.bars for f in folds)
    # Folds cobrem o dataset (menos o fold 0 pulado); total não excede len(prices)
    assert total_test_bars <= len(prices)

    # Agrega trades de todos os folds num BacktestResult sintético para MC
    all_trades: list[Trade] = []
    for f in folds:
        all_trades.extend(f.result.trades)

    if not all_trades:
        pytest.skip("nenhum trade em nenhum fold — dataset sintético não gerou trades")

    total_pnl = sum(t.pnl for t in all_trades)
    agg = BacktestResult(
        dataset_id=REFERENCE_DATASET_ID,
        bars=total_test_bars,
        fills=[],
        rejections=[],
        trades=all_trades,
        final_equity=10_000.0 + total_pnl,
        max_equity=10_000.0 + total_pnl,
        min_equity=10_000.0 + total_pnl,
        equity_curve=[(all_trades[0].entry_timestamp, 10_000.0)],
        metrics=BacktestMetrics(
            total_pnl=total_pnl,
            trade_count=len(all_trades),
            hit_rate=sum(1 for t in all_trades if t.pnl > 0) / len(all_trades),
            max_drawdown=0.0,
        ),
    )

    summary: MonteCarloSummary = monte_carlo_trades(
        result=agg, capital_inicial=10_000.0, n_resamples=500, seed=42
    )
    assert summary.n_resamples == 500
    assert summary.seed == 42
    keys = (5, 25, 50, 75, 95)
    fe_vals = [summary.final_equity_percentiles[k] for k in keys]
    assert fe_vals == sorted(fe_vals)
    dd_vals = [summary.max_drawdown_percentiles[k] for k in keys]
    assert dd_vals == sorted(dd_vals)
