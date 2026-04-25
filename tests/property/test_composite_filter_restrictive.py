"""Property-based: ``CompositeFilter`` AND/OR — monotonicidade **empírica** a nível de trade_count (ADR-0023).

⚠️ Este teste é uma propriedade **empírica fraca**, não estrutural. Sobre o dataset
sintético e grade de thresholds atuais, a invariante `len(trades(and(f1,f2))) <= min(...)`
é observada — mas o piloto H.5 sobre BTC Donchian real demonstrou que ela pode
**falhar** quando a engine fragmenta trades via EXIT mid-trade + re-entrada. A
invariante **forte** e correta, em nível de signal-emission bit-a-bit, está em
`test_composite_filter_signal_emission.py` e não depende da engine de execução.

Mantemos este teste para documentar a propriedade empírica + servir como canário
de regressão sobre o dataset sintético; mas não é a garantia formal do combinador.
"""

from __future__ import annotations

import pandas as pd
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.data.loaders import DatasetNotFoundError, load_dataset
from alpha_forge.regimes import (
    ATRRegimeFilter,
    CompositeFilter,
    SMASlopeFilter,
)
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.ma_crossover import MovingAverageCrossoverStrategy

REFERENCE_DATASET_ID = "synthetic_btcusdt_1h_seed42"


@pytest.fixture(scope="module")
def reference_prices() -> pd.DataFrame:
    try:
        return load_dataset(REFERENCE_DATASET_ID)
    except (DatasetNotFoundError, FileNotFoundError) as exc:
        pytest.skip(f"dataset seminal ausente: {exc}")


def _run(prices, regime_filter):
    return run_backtest(
        prices=prices,
        strategy=MovingAverageCrossoverStrategy(short_window=20, long_window=50),
        budget=RiskBudget(
            capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0
        ),
        cost_model=CostModel(taker_fee_bps=5.0, slippage_bps_per_unit_notional=10.0),
        dataset_id=REFERENCE_DATASET_ID,
        regime_filter=regime_filter,
    )


@settings(
    max_examples=6,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    min_slope_bps=st.floats(min_value=0.0, max_value=40.0, allow_nan=False),
    min_atr_bps=st.floats(min_value=0.0, max_value=100.0, allow_nan=False),
)
def test_and_is_strictly_more_restrictive(
    reference_prices: pd.DataFrame,
    min_slope_bps: float,
    min_atr_bps: float,
) -> None:
    sma = SMASlopeFilter(window=50, min_slope_bps=min_slope_bps)
    atr = ATRRegimeFilter(window=14, min_atr_bps=min_atr_bps)
    comp_and = CompositeFilter([sma, atr], mode="and")

    r_sma = _run(reference_prices, sma)
    r_atr = _run(reference_prices, atr)
    r_and = _run(reference_prices, comp_and)

    assert len(r_and.trades) <= len(r_sma.trades)
    assert len(r_and.trades) <= len(r_atr.trades)


@settings(
    max_examples=6,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    min_slope_bps=st.floats(min_value=0.0, max_value=40.0, allow_nan=False),
    min_atr_bps=st.floats(min_value=0.0, max_value=100.0, allow_nan=False),
)
def test_or_is_strictly_more_permissive(
    reference_prices: pd.DataFrame,
    min_slope_bps: float,
    min_atr_bps: float,
) -> None:
    sma = SMASlopeFilter(window=50, min_slope_bps=min_slope_bps)
    atr = ATRRegimeFilter(window=14, min_atr_bps=min_atr_bps)
    comp_or = CompositeFilter([sma, atr], mode="or")

    r_sma = _run(reference_prices, sma)
    r_atr = _run(reference_prices, atr)
    r_or = _run(reference_prices, comp_or)

    assert len(r_or.trades) >= len(r_sma.trades)
    assert len(r_or.trades) >= len(r_atr.trades)
