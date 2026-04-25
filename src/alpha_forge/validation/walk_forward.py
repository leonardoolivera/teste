"""Walk-forward causal (ADR-0003).

Divide o dataset em `N` folds contíguos e disjuntos; cada fold executa
`run_backtest` no `test_window`. Nenhum tuning de parâmetros — a estratégia
entra fixa. Tuning exige ADR própria.

Causalidade é herdada por construção: cada `test_window` é um `DataFrame`
recortado, e `run_backtest` aplica `assert_causal` internamente (ADR-0002).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import pandas as pd

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.engine import StrategyProtocol, run_backtest
from alpha_forge.risk.schemas import RiskBudget
from alpha_forge.validation.schemas import WalkForwardFold, WalkForwardWindow

if TYPE_CHECKING:
    from alpha_forge.regimes import RegimeFilter


class ValidationError(ValueError):
    """Erro de contrato de `validation/` (ADR-0003)."""


def walk_forward(
    *,
    prices: pd.DataFrame,
    strategy: StrategyProtocol,
    budget: RiskBudget,
    cost_model: CostModel,
    dataset_id: str,
    n_folds: int,
    scheme: Literal["rolling", "expanding"] = "rolling",
    train_fraction: float = 0.5,
    min_test_bars: int = 50,
    regime_filter: "RegimeFilter | None" = None,
) -> list[WalkForwardFold]:
    """Executa walk-forward causal e devolve lista de folds (ADR-0003).

    Partição:
      - O dataset é dividido em `n_folds` **janelas de teste** contíguas,
        disjuntas e do mesmo tamanho (última absorve o resto se não divide
        exatamente).
      - Para cada fold `k`, `train_window` é todo o passado anterior ao
        `test_window[k]`. `scheme="expanding"` retorna sempre do início;
        `scheme="rolling"` retorna uma janela fixa proporcional a
        `train_fraction * len(test_window)` antes do teste.
      - `test_start == train_end + 1 bar`; sem gap, sem overlap, sem shuffle.

    Validação:
      - `n_folds ≥ 2`.
      - `train_fraction ∈ (0, 1)`.
      - `min_test_bars ≥ 1`.
      - Cada `test_window` deve ter ≥ `min_test_bars` barras.
      - `rolling`: `train_window` deve ter ≥ 1 barra.
    """
    if n_folds < 2:
        raise ValidationError(f"n_folds deve ser >= 2 (recebido {n_folds})")
    if not (0.0 < train_fraction < 1.0):
        raise ValidationError(
            f"train_fraction deve estar em (0, 1) (recebido {train_fraction})"
        )
    if min_test_bars < 1:
        raise ValidationError(
            f"min_test_bars deve ser >= 1 (recebido {min_test_bars})"
        )
    if scheme not in ("rolling", "expanding"):
        raise ValidationError(
            f"scheme deve ser 'rolling' ou 'expanding' (recebido {scheme!r})"
        )

    n = len(prices)
    test_size = n // n_folds
    if test_size < min_test_bars:
        raise ValidationError(
            f"dataset curto: {n} barras em {n_folds} folds "
            f"dão test_size={test_size} < min_test_bars={min_test_bars}"
        )

    folds: list[WalkForwardFold] = []
    for k in range(n_folds):
        test_start_idx = k * test_size
        test_end_idx = (
            (k + 1) * test_size if k < n_folds - 1 else n
        )  # último fold absorve o resto

        if test_start_idx == 0:
            # Primeiro fold: não há train anterior; pulamos para respeitar
            # "train_window com ≥ 1 barra" — walk-forward clássico exige
            # sempre train antes de test.
            continue

        if scheme == "expanding":
            train_start_idx = 0
        else:  # rolling
            train_size = int(train_fraction * test_size)
            if train_size < 1:
                train_size = 1
            train_start_idx = max(0, test_start_idx - train_size)

        train_end_idx = test_start_idx  # exclusive

        train_slice = prices.iloc[train_start_idx:train_end_idx]
        test_slice = prices.iloc[test_start_idx:test_end_idx]

        if len(train_slice) < 1:
            raise ValidationError(
                f"fold {k}: train_window vazio (train_start={train_start_idx}, "
                f"train_end={train_end_idx})"
            )

        result = run_backtest(
            prices=test_slice,
            strategy=strategy,
            budget=budget,
            cost_model=cost_model,
            dataset_id=f"{dataset_id}#fold{k}",
            regime_filter=regime_filter,
        )

        train_window = WalkForwardWindow(
            start=train_slice.index[0].to_pydatetime(),
            end=train_slice.index[-1].to_pydatetime(),
            bars=len(train_slice),
        )
        test_window = WalkForwardWindow(
            start=test_slice.index[0].to_pydatetime(),
            end=test_slice.index[-1].to_pydatetime(),
            bars=len(test_slice),
        )
        folds.append(
            WalkForwardFold(
                fold_index=k,
                train_window=train_window,
                test_window=test_window,
                result=result,
            )
        )

    if not folds:
        raise ValidationError(
            f"nenhum fold gerado com n_folds={n_folds}; "
            f"fold 0 é sempre pulado por falta de train prévio"
        )

    return folds
