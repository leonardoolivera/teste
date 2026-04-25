"""Monotonicidade de custo isolada no componente `spread_bps` (ADR-0019).

Extensão da ADR-0010 ao terceiro componente do `CostModel`:

    Fixado o cenário (dataset + estratégia + budget + `taker_fee_bps` e
    `slippage_bps_per_unit_notional` constantes), se `spread_high > spread_low`
    e o cenário `low` gera ao menos um trade, então:

        final_equity_high <= final_equity_low + TOLERANCE

Spread é estrutural e independente de notional — a invariante vale sozinha,
sem acoplamento com os outros dois componentes. Os outros dois já são
cobertos por `test_cost_monotonicity.py`; aqui varia-se **somente spread**
para caracterizar o novo eixo.
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
from alpha_forge.strategies.families.ma_crossover import (
    MovingAverageCrossoverStrategy,
)

SPREAD_BPS_MAX = 100.0

REFERENCE_DATASET_ID = "synthetic_btcusdt_1h_seed42"
REFERENCE_SHORT_WINDOW = 20
REFERENCE_LONG_WINDOW = 50
REFERENCE_CAPITAL = 10_000.0
REFERENCE_FRACAO = 0.1
REFERENCE_ALAVANCAGEM = 2.0

# Fee e slip são fixos em valores plausíveis mas não-zero, garantindo que o
# baseline tem trades e que o teste isola estritamente o eixo de spread.
REFERENCE_FEE_BPS = 5.0
REFERENCE_SLIP_BPS = 2.0

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
        strategy=MovingAverageCrossoverStrategy(
            short_window=REFERENCE_SHORT_WINDOW, long_window=REFERENCE_LONG_WINDOW
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
def dominated_spread_pair(draw: st.DrawFn) -> tuple[CostModel, CostModel]:
    """Gera `(cost_low, cost_high)` variando **só** `spread_bps`.

    Fee e slip são idênticos nos dois modelos; somente `spread_high` domina
    `spread_low` por construção com delta ≥ 1e-9 — mesma lógica anti-flaky
    do composite do sibling `test_cost_monotonicity.py`.
    """
    spread_low = draw(
        st.floats(
            min_value=0.0,
            max_value=SPREAD_BPS_MAX,
            allow_nan=False,
            allow_infinity=False,
        )
    )
    spread_delta = draw(
        st.floats(
            min_value=1e-9,
            max_value=max(1e-9, SPREAD_BPS_MAX - spread_low),
            allow_nan=False,
            allow_infinity=False,
        )
    )
    cost_low = CostModel(
        taker_fee_bps=REFERENCE_FEE_BPS,
        slippage_bps_per_unit_notional=REFERENCE_SLIP_BPS,
        spread_bps=spread_low,
    )
    cost_high = CostModel(
        taker_fee_bps=REFERENCE_FEE_BPS,
        slippage_bps_per_unit_notional=REFERENCE_SLIP_BPS,
        spread_bps=spread_low + spread_delta,
    )
    return cost_low, cost_high


@given(cost_pair=dominated_spread_pair())
@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_spread_monotonicity_in_final_equity(
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
        "Violação de monotonicidade de spread (ADR-0019 + ADR-0010): "
        "spread maior produziu final_equity maior.\n"
        f"  spread_low  = {cost_low.spread_bps:.6f}\n"
        f"  spread_high = {cost_high.spread_bps:.6f}\n"
        f"  final_equity_low  = {final_low:.10f}\n"
        f"  final_equity_high = {final_high:.10f}\n"
        f"  delta (high - low) = {delta:.10f} "
        f"(tolerance = {FINAL_EQUITY_TOLERANCE:.10f})\n"
        f"  trade_count_low  = {result_low.metrics.trade_count}\n"
        f"  trade_count_high = {result_high.metrics.trade_count}"
    )
