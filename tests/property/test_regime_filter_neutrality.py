"""Property-based: filtro sempre-ativo preserva bit-a-bit ADR-0022.

Invariante: quando o ``regime_filter`` retorna ``True`` para toda barra,
``run_backtest(...)`` deve produzir resultado **bit-a-bit idêntico** ao
``run_backtest(...)`` sem filtro (``regime_filter=None``). Garante que a
introdução do parâmetro opcional de ADR-0022 não quebra reprodutibilidade
de corridas anteriores.
"""

from __future__ import annotations

import pandas as pd
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.data.loaders import DatasetNotFoundError, load_dataset
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.ma_crossover import MovingAverageCrossoverStrategy

REFERENCE_DATASET_ID = "synthetic_btcusdt_1h_seed42"
REFERENCE_SHORT = 20
REFERENCE_LONG = 50
REFERENCE_CAPITAL = 10_000.0


class _AlwaysActive:
    name = "always_active"

    def is_active(self, window: pd.DataFrame) -> bool:
        return True


@pytest.fixture(scope="module")
def reference_prices() -> pd.DataFrame:
    try:
        return load_dataset(REFERENCE_DATASET_ID)
    except (DatasetNotFoundError, FileNotFoundError) as exc:
        pytest.skip(
            f"dataset seminal '{REFERENCE_DATASET_ID}' ausente: {exc}"
        )


@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    fee_bps=st.floats(min_value=0.0, max_value=20.0, allow_nan=False),
    slip_bps=st.floats(min_value=0.0, max_value=50.0, allow_nan=False),
)
def test_always_active_filter_identical_to_none(
    reference_prices: pd.DataFrame, fee_bps: float, slip_bps: float
) -> None:
    cost_model = CostModel(
        taker_fee_bps=fee_bps, slippage_bps_per_unit_notional=slip_bps
    )
    budget = RiskBudget(
        capital_inicial=REFERENCE_CAPITAL,
        fracao_por_trade=0.1,
        alavancagem_max=2.0,
    )
    strategy = MovingAverageCrossoverStrategy(
        short_window=REFERENCE_SHORT, long_window=REFERENCE_LONG
    )

    result_none = run_backtest(
        prices=reference_prices,
        strategy=strategy,
        budget=budget,
        cost_model=cost_model,
        dataset_id=REFERENCE_DATASET_ID,
        regime_filter=None,
    )
    result_always = run_backtest(
        prices=reference_prices,
        strategy=strategy,
        budget=budget,
        cost_model=cost_model,
        dataset_id=REFERENCE_DATASET_ID,
        regime_filter=_AlwaysActive(),
    )

    # Bit-a-bit: final_equity, trade_count, fills count, rejections count.
    assert result_none.final_equity == result_always.final_equity
    assert len(result_none.fills) == len(result_always.fills)
    assert len(result_none.trades) == len(result_always.trades)
    assert len(result_none.rejections) == len(result_always.rejections)
    assert result_none.metrics.total_pnl == result_always.metrics.total_pnl
    assert result_none.metrics.max_drawdown == result_always.metrics.max_drawdown
