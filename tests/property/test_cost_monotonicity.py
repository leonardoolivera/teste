"""Property-based test de monotonicidade de custo (ADR-0010).

Invariante central:

    Fixado o cenário (mesmo dataset, mesma estratégia, mesmo RiskBudget,
    mesmo dataset_id), se ``cost_high`` domina ``cost_low`` componente a
    componente (com pelo menos uma desigualdade estrita) e o cenário `low`
    gera ao menos um trade, então:

        final_equity_high <= final_equity_low + TOLERANCE

Só ``final_equity``. Não ``total_pnl`` (aritmeticamente equivalente, menos
visível), não ``hit_rate`` nem ``max_drawdown`` (não-monotônicas por efeito
de ordem — ver ADR-0010 §Ressalvas).

Estratégia de referência: MovingAverageCrossoverStrategy(20, 50) sobre o
dataset sintético seminal (`synthetic_btcusdt_1h_seed42`).
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

# ADR-0010: estratégia, dataset e budget são parte do cenário fixo.
REFERENCE_DATASET_ID = "synthetic_btcusdt_1h_seed42"
REFERENCE_SHORT_WINDOW = 20
REFERENCE_LONG_WINDOW = 50
REFERENCE_CAPITAL = 10_000.0
REFERENCE_FRACAO = 0.1
REFERENCE_ALAVANCAGEM = 2.0

# Tolerância numérica absoluta, em unidades de ``capital_inicial``.
# ADR-0010: `1e-6 * capital_inicial` absorve ruído de ponto flutuante sem
# mascarar bug de sinal. Escolhido fixo (não relativo a final_equity) para
# evitar degradação silenciosa em cenários de drawdown grande.
FINAL_EQUITY_TOLERANCE = 1e-6 * REFERENCE_CAPITAL


@pytest.fixture(scope="module")
def reference_prices() -> pd.DataFrame:
    """Dataset sintético seminal. Pula toda a suíte se ainda não foi bootstrapado."""
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


def _dominates(high: CostModel, low: CostModel) -> bool:
    """`high` domina `low` componente a componente, com ≥1 desigualdade estrita."""
    ge_fee = high.taker_fee_bps >= low.taker_fee_bps
    ge_slip = (
        high.slippage_bps_per_unit_notional >= low.slippage_bps_per_unit_notional
    )
    strict = (
        high.taker_fee_bps > low.taker_fee_bps
        or high.slippage_bps_per_unit_notional > low.slippage_bps_per_unit_notional
    )
    return ge_fee and ge_slip and strict


@given(
    fee_low=st.floats(
        min_value=0.0, max_value=50.0, allow_nan=False, allow_infinity=False
    ),
    fee_high=st.floats(
        min_value=0.0, max_value=50.0, allow_nan=False, allow_infinity=False
    ),
    slip_low=st.floats(
        min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False
    ),
    slip_high=st.floats(
        min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False
    ),
)
@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_cost_monotonicity_in_final_equity(
    reference_prices: pd.DataFrame,
    fee_low: float,
    fee_high: float,
    slip_low: float,
    slip_high: float,
) -> None:
    cost_low = CostModel(
        taker_fee_bps=fee_low, slippage_bps_per_unit_notional=slip_low
    )
    cost_high = CostModel(
        taker_fee_bps=fee_high, slippage_bps_per_unit_notional=slip_high
    )

    # ADR-0010: invariante só é definida quando cost_high domina cost_low
    # componente a componente, com ao menos uma desigualdade estrita.
    assume(_dominates(cost_high, cost_low))

    result_low = _run(reference_prices, cost_low)
    result_high = _run(reference_prices, cost_high)

    # ADR-0010 §Ressalva 1: se o cenário `low` não entrou em posição,
    # custo é irrelevante — fora do domínio da invariante.
    assert result_low.metrics is not None
    assert result_high.metrics is not None
    assume(result_low.metrics.trade_count > 0)

    final_low = result_low.final_equity
    final_high = result_high.final_equity
    delta = final_high - final_low

    assert delta <= FINAL_EQUITY_TOLERANCE, (
        "Violação de monotonicidade de custo (ADR-0010): "
        "custo maior produziu final_equity maior.\n"
        f"  cost_low  = taker_fee_bps={cost_low.taker_fee_bps:.6f} "
        f"slippage_bps_per_unit_notional={cost_low.slippage_bps_per_unit_notional:.6f}\n"
        f"  cost_high = taker_fee_bps={cost_high.taker_fee_bps:.6f} "
        f"slippage_bps_per_unit_notional={cost_high.slippage_bps_per_unit_notional:.6f}\n"
        f"  final_equity_low  = {final_low:.10f}\n"
        f"  final_equity_high = {final_high:.10f}\n"
        f"  delta (high - low) = {delta:.10f} (tolerance = {FINAL_EQUITY_TOLERANCE:.10f})\n"
        f"  trade_count_low  = {result_low.metrics.trade_count}\n"
        f"  trade_count_high = {result_high.metrics.trade_count}\n"
        f"  fills_low  = {len(result_low.fills)}\n"
        f"  fills_high = {len(result_high.fills)}"
    )
