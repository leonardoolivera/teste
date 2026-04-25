"""Property-based test de monotonicidade de custo para `BollingerMeanReversionStrategy`.

Aplicação mecânica do invariante ADR-0010 + ADR-0019 à quinta família do
laboratório (ADR-0026). Varia-se os 3 eixos de custo (fee, slippage, spread)
conjuntamente — com pelo menos uma desigualdade estrita por par.

Invariante:

    Fixado o cenário (mesmo dataset + estratégia + budget + `dataset_id`), se
    ``cost_high`` domina ``cost_low`` componente a componente nos 3 eixos
    (fee, slip, spread), com pelo menos uma desigualdade estrita, e o cenário
    `low` gera ao menos um trade, então:

        final_equity_high <= final_equity_low + TOLERANCE

Estratégia de referência: `BollingerMeanReversionStrategy(window=20, num_std=2.0)`
sobre o dataset sintético seminal.
"""

from __future__ import annotations

import pandas as pd
import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import run_backtest
from alpha_forge.backtest.schemas import BacktestResult
from alpha_forge.data.loaders import DatasetNotFoundError, load_dataset
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.bollinger import BollingerMeanReversionStrategy

FEE_BPS_MAX = 50.0
SLIP_BPS_MAX = 100.0
SPREAD_BPS_MAX = 100.0

REFERENCE_DATASET_ID = "synthetic_btcusdt_1h_seed42"
REFERENCE_WINDOW = 20
REFERENCE_NUM_STD = 2.0
REFERENCE_CAPITAL = 10_000.0
REFERENCE_FRACAO = 0.1
REFERENCE_ALAVANCAGEM = 2.0

FINAL_EQUITY_TOLERANCE = 1e-6 * REFERENCE_CAPITAL


@pytest.fixture(scope="module")
def reference_prices() -> pd.DataFrame:
    try:
        return load_dataset(REFERENCE_DATASET_ID)
    except (DatasetNotFoundError, FileNotFoundError) as exc:
        pytest.skip(
            f"dataset seminal '{REFERENCE_DATASET_ID}' ausente "
            f"(rode `uv run python scripts/bootstrap_synthetic_dataset.py`): {exc}"
        )


def _run(prices: pd.DataFrame, cost_model: CostModel) -> BacktestResult:
    return run_backtest(
        prices=prices,
        strategy=BollingerMeanReversionStrategy(
            window=REFERENCE_WINDOW, num_std=REFERENCE_NUM_STD
        ),
        budget=RiskBudget(
            capital_inicial=REFERENCE_CAPITAL,
            fracao_por_trade=REFERENCE_FRACAO,
            alavancagem_max=REFERENCE_ALAVANCAGEM,
        ),
        cost_model=cost_model,
        dataset_id=REFERENCE_DATASET_ID,
    )


@st.composite
def dominated_cost_pair(draw: st.DrawFn) -> tuple[CostModel, CostModel]:
    fee_low = draw(
        st.floats(min_value=0.0, max_value=FEE_BPS_MAX, allow_nan=False, allow_infinity=False)
    )
    slip_low = draw(
        st.floats(min_value=0.0, max_value=SLIP_BPS_MAX, allow_nan=False, allow_infinity=False)
    )
    spread_low = draw(
        st.floats(min_value=0.0, max_value=SPREAD_BPS_MAX, allow_nan=False, allow_infinity=False)
    )
    fee_delta = draw(
        st.floats(min_value=0.0, max_value=FEE_BPS_MAX - fee_low, allow_nan=False, allow_infinity=False)
    )
    slip_delta = draw(
        st.floats(min_value=0.0, max_value=SLIP_BPS_MAX - slip_low, allow_nan=False, allow_infinity=False)
    )
    spread_delta = draw(
        st.floats(min_value=0.0, max_value=SPREAD_BPS_MAX - spread_low, allow_nan=False, allow_infinity=False)
    )
    if fee_delta == 0.0 and slip_delta == 0.0 and spread_delta == 0.0:
        spread_delta = draw(
            st.floats(
                min_value=1e-9,
                max_value=max(1e-9, SPREAD_BPS_MAX - spread_low),
                allow_nan=False,
                allow_infinity=False,
            )
        )
    cost_low = CostModel(
        taker_fee_bps=fee_low,
        slippage_bps_per_unit_notional=slip_low,
        spread_bps=spread_low,
    )
    cost_high = CostModel(
        taker_fee_bps=fee_low + fee_delta,
        slippage_bps_per_unit_notional=slip_low + slip_delta,
        spread_bps=spread_low + spread_delta,
    )
    return cost_low, cost_high


@given(cost_pair=dominated_cost_pair())
@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_cost_monotonicity_bollinger_in_final_equity(
    reference_prices: pd.DataFrame,
    cost_pair: tuple[CostModel, CostModel],
) -> None:
    cost_low, cost_high = cost_pair

    result_low = _run(reference_prices, cost_low)
    result_high = _run(reference_prices, cost_high)

    assert result_low.metrics is not None
    assert result_high.metrics is not None
    assume(result_low.metrics.trade_count > 0)

    final_low = result_low.final_equity
    final_high = result_high.final_equity
    delta = final_high - final_low

    assert delta <= FINAL_EQUITY_TOLERANCE, (
        "Violação de monotonicidade de custo (ADR-0010 + ADR-0019 aplicados a Bollinger): "
        "custo maior produziu final_equity maior.\n"
        f"  strategy = BollingerMeanReversionStrategy(window={REFERENCE_WINDOW}, "
        f"num_std={REFERENCE_NUM_STD})\n"
        f"  cost_low  = fee={cost_low.taker_fee_bps:.6f} "
        f"slip={cost_low.slippage_bps_per_unit_notional:.6f} "
        f"spread={cost_low.spread_bps:.6f}\n"
        f"  cost_high = fee={cost_high.taker_fee_bps:.6f} "
        f"slip={cost_high.slippage_bps_per_unit_notional:.6f} "
        f"spread={cost_high.spread_bps:.6f}\n"
        f"  final_equity_low  = {final_low:.10f}\n"
        f"  final_equity_high = {final_high:.10f}\n"
        f"  delta (high - low) = {delta:.10f} (tolerance = {FINAL_EQUITY_TOLERANCE:.10f})\n"
        f"  trade_count_low  = {result_low.metrics.trade_count}\n"
        f"  trade_count_high = {result_high.metrics.trade_count}"
    )
