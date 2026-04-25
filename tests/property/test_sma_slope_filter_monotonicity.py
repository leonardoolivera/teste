"""Property-based: ``SMASlopeFilter`` é monotônico em ``min_slope_bps``.

Invariante (ADR-0022 §3): aumentar ``min_slope_bps`` torna o filtro
**estritamente mais restritivo**. Como o engine coage ``is_active=False``
em ``HOLD``/``EXIT``, o número de ``trades`` de ``run_backtest(...)`` com
``min_slope_bps=b1 >= b0`` **nunca** pode exceder o número de trades com
``min_slope_bps=b0``.

Ou seja: ``len(trades(b1)) <= len(trades(b0))`` sempre que ``b1 >= b0``.
"""

from __future__ import annotations

import pandas as pd
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.data.loaders import DatasetNotFoundError, load_dataset
from alpha_forge.regimes import SMASlopeFilter
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
    sma_window=st.integers(min_value=10, max_value=50),
    slope_low=st.floats(min_value=0.0, max_value=20.0, allow_nan=False),
    slope_delta=st.floats(min_value=0.0, max_value=80.0, allow_nan=False),
)
def test_monotonicity_min_slope_bps(
    reference_prices: pd.DataFrame,
    sma_window: int,
    slope_low: float,
    slope_delta: float,
) -> None:
    slope_high = slope_low + slope_delta

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
        regime_filter=SMASlopeFilter(window=sma_window, min_slope_bps=slope_low),
    )
    result_high = run_backtest(
        prices=reference_prices,
        strategy=strategy,
        budget=budget,
        cost_model=cost_model,
        dataset_id=REFERENCE_DATASET_ID,
        regime_filter=SMASlopeFilter(window=sma_window, min_slope_bps=slope_high),
    )

    assert len(result_high.trades) <= len(result_low.trades)
