"""Property-based: walk-forward preserva causalidade por construção (ADR-0003).

Invariante:

    Fixado o cenário (mesmo dataset, mesma estratégia, mesmo budget, mesmo
    cost_model, mesmo n_folds, mesmo scheme), mutar as barras dentro do
    test_window[k] **não** altera o `result[j]` para `j < k`.

Isso é derivado de ADR-0002 (execução causal) no nível de `run_backtest`;
aqui verificamos que a composição `walk_forward` (múltiplos backtests sobre
fatias disjuntas) preserva a propriedade explicitamente.
"""

from __future__ import annotations

import pandas as pd
import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from alpha_forge.backtest.cost import zero_cost
from alpha_forge.data.loaders import DatasetNotFoundError, load_dataset
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.ma_crossover import (
    MovingAverageCrossoverStrategy,
)
from alpha_forge.validation import walk_forward

REFERENCE_DATASET_ID = "synthetic_btcusdt_1h_seed42"


@pytest.fixture(scope="module")
def prices() -> pd.DataFrame:
    try:
        return load_dataset(REFERENCE_DATASET_ID)
    except (DatasetNotFoundError, FileNotFoundError) as exc:
        pytest.skip(f"dataset seminal ausente: {exc}")


@given(
    mutation_bar_offset=st.integers(min_value=0, max_value=50),
    mutation_factor=st.floats(
        min_value=0.5, max_value=2.0, allow_nan=False, allow_infinity=False
    ),
)
@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_mutar_fold_futuro_nao_afeta_fold_passado(
    prices: pd.DataFrame,
    mutation_bar_offset: int,
    mutation_factor: float,
) -> None:
    """Mutar barras dentro de test_window[k] não altera result[j] para j < k."""
    strategy = MovingAverageCrossoverStrategy(short_window=20, long_window=50)
    budget = RiskBudget(
        capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0
    )
    n_folds = 5

    folds_original = walk_forward(
        prices=prices,
        strategy=strategy,
        budget=budget,
        cost_model=zero_cost(),
        dataset_id=REFERENCE_DATASET_ID,
        n_folds=n_folds,
        min_test_bars=50,
    )
    assume(len(folds_original) >= 2)

    # Escolhe o último fold para mutar — garante que existe fold anterior
    target_fold = folds_original[-1]
    target_start_ts = target_fold.test_window.start
    target_start_idx = prices.index.get_loc(pd.Timestamp(target_start_ts))
    mutate_idx = min(target_start_idx + mutation_bar_offset, len(prices) - 1)
    assume(mutate_idx >= target_start_idx)

    mutated = prices.copy()
    for col in ("open", "high", "low", "close"):
        mutated.iloc[mutate_idx, mutated.columns.get_loc(col)] *= mutation_factor
    # Mantém OHLC válido
    row = mutated.iloc[mutate_idx]
    h = max(row["open"], row["high"], row["close"])
    l = min(row["open"], row["low"], row["close"])
    mutated.iloc[mutate_idx, mutated.columns.get_loc("high")] = h
    mutated.iloc[mutate_idx, mutated.columns.get_loc("low")] = l

    folds_mutated = walk_forward(
        prices=mutated,
        strategy=strategy,
        budget=budget,
        cost_model=zero_cost(),
        dataset_id=REFERENCE_DATASET_ID,
        n_folds=n_folds,
        min_test_bars=50,
    )

    # Todos os folds anteriores ao último devem ser idênticos
    for f_orig, f_mut in zip(folds_original[:-1], folds_mutated[:-1]):
        assert f_orig.fold_index == f_mut.fold_index
        assert f_orig.result.final_equity == f_mut.result.final_equity, (
            f"fold {f_orig.fold_index}: mutar barra {mutate_idx} no último fold "
            f"alterou final_equity do fold anterior — violação de causalidade."
        )
        assert len(f_orig.result.trades) == len(f_mut.result.trades)
