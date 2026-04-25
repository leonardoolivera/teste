"""Property-based: ``BollingerWidthFilter`` é monotônico em ``min_width_bps``.

Invariante: aumentar ``min_width_bps`` torna o filtro estritamente mais
restritivo → ``len(trades(b1)) <= len(trades(b0))`` sempre que b1 >= b0.
"""

from __future__ import annotations

import pandas as pd
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.data.loaders import DatasetNotFoundError, load_dataset
from alpha_forge.regimes import BollingerWidthFilter
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.ma_crossover import MovingAverageCrossoverStrategy

REFERENCE_DATASET_ID = "synthetic_btcusdt_1h_seed42"


@pytest.fixture(scope="module")
def reference_prices() -> pd.DataFrame:
    try:
        return load_dataset(REFERENCE_DATASET_ID)
    except (DatasetNotFoundError, FileNotFoundError) as exc:
        pytest.skip(
            f"dataset seminal '{REFERENCE_DATASET_ID}' ausente: {exc}"
        )


@settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    bw_window=st.integers(min_value=10, max_value=30),
    num_std=st.floats(min_value=1.0, max_value=2.5, allow_nan=False),
    width_low=st.floats(min_value=0.0, max_value=50.0, allow_nan=False),
    width_delta=st.floats(min_value=0.0, max_value=500.0, allow_nan=False),
)
def test_monotonicity_min_width_bps(
    reference_prices: pd.DataFrame,
    bw_window: int,
    num_std: float,
    width_low: float,
    width_delta: float,
) -> None:
    width_high = width_low + width_delta

    cost_model = CostModel(taker_fee_bps=5.0, slippage_bps_per_unit_notional=10.0)
    budget = RiskBudget(
        capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0
    )
    strategy = MovingAverageCrossoverStrategy(short_window=20, long_window=50)

    result_low = run_backtest(
        prices=reference_prices,
        strategy=strategy,
        budget=budget,
        cost_model=cost_model,
        dataset_id=REFERENCE_DATASET_ID,
        regime_filter=BollingerWidthFilter(
            window=bw_window, num_std=num_std, min_width_bps=width_low
        ),
    )
    result_high = run_backtest(
        prices=reference_prices,
        strategy=strategy,
        budget=budget,
        cost_model=cost_model,
        dataset_id=REFERENCE_DATASET_ID,
        regime_filter=BollingerWidthFilter(
            window=bw_window, num_std=num_std, min_width_bps=width_high
        ),
    )

    assert len(result_high.trades) <= len(result_low.trades)
