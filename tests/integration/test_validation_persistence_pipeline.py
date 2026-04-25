"""Integration: pipeline `validation/` + persistência end-to-end (ADR-0015).

Roda `walk_forward` + `monte_carlo_trades` + `cost_stress` sobre MA 20/50 no
sintético seminal; persiste os três artefatos em `tmp_path`; carrega de
volta; verifica round-trip estrutural (final_equity, trade_count, percentis).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.schemas import BacktestMetrics, BacktestResult, Trade
from alpha_forge.data.loaders import DatasetNotFoundError, load_dataset
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.ma_crossover import (
    MovingAverageCrossoverStrategy,
)
from alpha_forge.validation import (
    CostPerturbation,
    cost_stress,
    load_cost_stress_report,
    load_monte_carlo_summary,
    load_walk_forward_folds,
    monte_carlo_trades,
    save_cost_stress_report,
    save_monte_carlo_summary,
    save_walk_forward_folds,
    walk_forward,
)

REFERENCE_DATASET_ID = "synthetic_btcusdt_1h_seed42"


@pytest.fixture(scope="module")
def prices() -> pd.DataFrame:
    try:
        return load_dataset(REFERENCE_DATASET_ID)
    except (DatasetNotFoundError, FileNotFoundError) as exc:
        pytest.skip(f"dataset seminal ausente: {exc}")


def test_pipeline_completo_round_trip(prices: pd.DataFrame, tmp_path: Path) -> None:
    strategy = MovingAverageCrossoverStrategy(short_window=20, long_window=50)
    budget = RiskBudget(
        capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0
    )
    cost_model = CostModel(taker_fee_bps=5.0, slippage_bps_per_unit_notional=2.0)

    folds = walk_forward(
        prices=prices,
        strategy=strategy,
        budget=budget,
        cost_model=cost_model,
        dataset_id=REFERENCE_DATASET_ID,
        n_folds=5,
        scheme="rolling",
        train_fraction=0.5,
        min_test_bars=50,
    )

    all_trades: list[Trade] = []
    for f in folds:
        all_trades.extend(f.result.trades)

    if not all_trades:
        pytest.skip("nenhum trade em nenhum fold")

    total_pnl = sum(t.pnl for t in all_trades)
    agg = BacktestResult(
        dataset_id=REFERENCE_DATASET_ID,
        bars=sum(f.test_window.bars for f in folds),
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
    mc = monte_carlo_trades(
        result=agg, capital_inicial=10_000.0, n_resamples=500, seed=42
    )

    stress = cost_stress(
        prices=prices,
        strategy=strategy,
        budget=budget,
        baseline_cost=cost_model,
        perturbations=[
            CostPerturbation(label="fee+10", fee_delta_bps=10.0, slip_delta_bps=0.0),
            CostPerturbation(label="slip+10", fee_delta_bps=0.0, slip_delta_bps=10.0),
        ],
        dataset_id=REFERENCE_DATASET_ID,
    )

    run_dir = tmp_path / "run_pipeline_test"
    save_walk_forward_folds(folds=folds, directory=run_dir)
    save_monte_carlo_summary(summary=mc, directory=run_dir)
    save_cost_stress_report(report=stress, directory=run_dir)

    assert (run_dir / "walk_forward.json").exists()
    assert (run_dir / "monte_carlo.json").exists()
    assert (run_dir / "cost_stress.json").exists()

    loaded_folds = load_walk_forward_folds(directory=run_dir)
    loaded_mc = load_monte_carlo_summary(directory=run_dir)
    loaded_stress = load_cost_stress_report(directory=run_dir)

    # Round-trip estrutural: pydantic __eq__ em objetos frozen é comparação de campos.
    assert loaded_folds == folds
    assert loaded_mc == mc
    assert loaded_stress == stress

    # Spot checks defensivos (não redundantes com __eq__ — documentam invariante útil).
    assert len(loaded_folds) == len(folds)
    for lf, f in zip(loaded_folds, folds):
        assert lf.result.final_equity == f.result.final_equity
        assert lf.result.metrics is not None and f.result.metrics is not None
        assert lf.result.metrics.trade_count == f.result.metrics.trade_count
    assert loaded_mc.seed == 42
    assert set(loaded_mc.final_equity_percentiles.keys()) == {5, 25, 50, 75, 95}
    assert len(loaded_stress.scenarios) == 2
    assert [s.label for s in loaded_stress.scenarios] == ["fee+10", "slip+10"]
