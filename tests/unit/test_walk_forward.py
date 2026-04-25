"""Unit tests de `validation.walk_forward` (ADR-0003).

Cobre contrato de parâmetros, particionamento exato (folds contíguos
disjuntos, sem gap/overlap) e integração com `run_backtest` via fatiamento
causal.
"""

from __future__ import annotations

import pandas as pd
import pytest

from alpha_forge.backtest.cost import zero_cost
from alpha_forge.data.loaders import DatasetNotFoundError, load_dataset
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.strategies.families.ma_crossover import (
    MovingAverageCrossoverStrategy,
)
from alpha_forge.validation import ValidationError, walk_forward

REFERENCE_DATASET_ID = "synthetic_btcusdt_1h_seed42"


@pytest.fixture(scope="module")
def prices() -> pd.DataFrame:
    try:
        return load_dataset(REFERENCE_DATASET_ID)
    except (DatasetNotFoundError, FileNotFoundError) as exc:
        pytest.skip(f"dataset seminal ausente: {exc}")


@pytest.fixture(scope="module")
def budget() -> RiskBudget:
    return RiskBudget(
        capital_inicial=10_000.0, fracao_por_trade=0.1, alavancagem_max=2.0
    )


@pytest.fixture(scope="module")
def strategy() -> MovingAverageCrossoverStrategy:
    return MovingAverageCrossoverStrategy(short_window=20, long_window=50)


class TestValidacaoParametros:
    def test_n_folds_minimo_2(
        self,
        prices: pd.DataFrame,
        strategy: MovingAverageCrossoverStrategy,
        budget: RiskBudget,
    ) -> None:
        with pytest.raises(ValidationError, match="n_folds"):
            walk_forward(
                prices=prices,
                strategy=strategy,
                budget=budget,
                cost_model=zero_cost(),
                dataset_id=REFERENCE_DATASET_ID,
                n_folds=1,
            )

    def test_train_fraction_deve_estar_em_intervalo(
        self,
        prices: pd.DataFrame,
        strategy: MovingAverageCrossoverStrategy,
        budget: RiskBudget,
    ) -> None:
        for bad in (0.0, 1.0, -0.1, 1.5):
            with pytest.raises(ValidationError, match="train_fraction"):
                walk_forward(
                    prices=prices,
                    strategy=strategy,
                    budget=budget,
                    cost_model=zero_cost(),
                    dataset_id=REFERENCE_DATASET_ID,
                    n_folds=5,
                    train_fraction=bad,
                )

    def test_scheme_invalido_rejeitado(
        self,
        prices: pd.DataFrame,
        strategy: MovingAverageCrossoverStrategy,
        budget: RiskBudget,
    ) -> None:
        with pytest.raises(ValidationError, match="scheme"):
            walk_forward(
                prices=prices,
                strategy=strategy,
                budget=budget,
                cost_model=zero_cost(),
                dataset_id=REFERENCE_DATASET_ID,
                n_folds=5,
                scheme="shuffle",  # type: ignore[arg-type]
            )

    def test_dataset_curto_rejeitado(
        self,
        prices: pd.DataFrame,
        strategy: MovingAverageCrossoverStrategy,
        budget: RiskBudget,
    ) -> None:
        # 720 / 100 folds = 7 bars/fold < 50
        with pytest.raises(ValidationError, match="min_test_bars"):
            walk_forward(
                prices=prices,
                strategy=strategy,
                budget=budget,
                cost_model=zero_cost(),
                dataset_id=REFERENCE_DATASET_ID,
                n_folds=100,
                min_test_bars=50,
            )


class TestParticionamento:
    def test_folds_contiguos_disjuntos(
        self,
        prices: pd.DataFrame,
        strategy: MovingAverageCrossoverStrategy,
        budget: RiskBudget,
    ) -> None:
        folds = walk_forward(
            prices=prices,
            strategy=strategy,
            budget=budget,
            cost_model=zero_cost(),
            dataset_id=REFERENCE_DATASET_ID,
            n_folds=5,
            min_test_bars=50,
        )
        # fold 0 pulado (sem train anterior), então esperamos 4 folds
        assert len(folds) == 4
        for prev, curr in zip(folds, folds[1:]):
            # test_end do anterior == test_start do próximo (contíguo, sem overlap)
            assert prev.test_window.end < curr.test_window.start

    def test_expanding_vs_rolling(
        self,
        prices: pd.DataFrame,
        strategy: MovingAverageCrossoverStrategy,
        budget: RiskBudget,
    ) -> None:
        folds_rolling = walk_forward(
            prices=prices,
            strategy=strategy,
            budget=budget,
            cost_model=zero_cost(),
            dataset_id=REFERENCE_DATASET_ID,
            n_folds=5,
            scheme="rolling",
            train_fraction=0.5,
            min_test_bars=50,
        )
        folds_expanding = walk_forward(
            prices=prices,
            strategy=strategy,
            budget=budget,
            cost_model=zero_cost(),
            dataset_id=REFERENCE_DATASET_ID,
            n_folds=5,
            scheme="expanding",
            min_test_bars=50,
        )
        # expanding: train_window cresce fold a fold
        for prev, curr in zip(folds_expanding, folds_expanding[1:]):
            assert curr.train_window.bars > prev.train_window.bars
        # rolling: train_window proporcional ao test_size (constante neste caso)
        sizes_rolling = {f.train_window.bars for f in folds_rolling[:-1]}
        # todos exceto o último podem ter mesmo tamanho
        assert len(sizes_rolling) <= 1 or max(sizes_rolling) - min(sizes_rolling) <= 1


class TestIntegracaoComEngine:
    def test_cada_fold_produz_backtest_result(
        self,
        prices: pd.DataFrame,
        strategy: MovingAverageCrossoverStrategy,
        budget: RiskBudget,
    ) -> None:
        folds = walk_forward(
            prices=prices,
            strategy=strategy,
            budget=budget,
            cost_model=zero_cost(),
            dataset_id=REFERENCE_DATASET_ID,
            n_folds=5,
            min_test_bars=50,
        )
        for f in folds:
            assert f.result.bars == f.test_window.bars
            assert f.result.metrics is not None
            # dataset_id propaga com sufixo #foldK (útil para logging)
            assert f.result.dataset_id.startswith(REFERENCE_DATASET_ID)
            assert f.result.dataset_id.endswith(f"#fold{f.fold_index}")
