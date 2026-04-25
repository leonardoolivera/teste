"""Contratos de I/O do módulo de validação (ADR-0003).

Dois tipos: `WalkForwardFold` (uma janela train/test do walk-forward) e
`MonteCarloSummary` (resultado agregado de um resampling sobre trades).

Ambos são `frozen` e `extra="forbid"` — mesma rigidez contratual dos outros
schemas do laboratório (ADR-0002 §reprodutibilidade).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from alpha_forge.backtest.cost import CostModel
from alpha_forge.backtest.schemas import BacktestResult


class WalkForwardWindow(BaseModel):
    """Janela temporal (train ou test) do walk-forward."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    start: datetime
    end: datetime
    bars: int = Field(ge=0)


class WalkForwardFold(BaseModel):
    """Um fold do walk-forward: train + test + resultado do backtest no test.

    `train_window` existe estruturalmente mesmo sem tuning — reserva o contrato
    para quando uma ADR futura de optimização entrar (ADR-0003 §"Decision").
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    fold_index: int = Field(ge=0)
    train_window: WalkForwardWindow
    test_window: WalkForwardWindow
    result: BacktestResult


class MonteCarloSummary(BaseModel):
    """Resultado agregado de `n_resamples` reamostragens de PnL de trades.

    Percentis são chaves fixas `{5, 25, 50, 75, 95}` — conjunto escolhido para
    dar visão de cauda + mediana sem explodir superfície. Não acrescentar
    percentis aqui sem ADR; composite scoring e ranking são explicitamente
    deferred (ADR-0003 §"Não entra neste núcleo mínimo").
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    n_resamples: int = Field(ge=100)
    seed: int
    final_equity_percentiles: dict[int, float]
    max_drawdown_percentiles: dict[int, float]
    original_final_equity: float
    original_max_drawdown: float


class CostPerturbation(BaseModel):
    """Delta absoluto aditivo em bps aplicado sobre um `CostModel` baseline (ADR-0014).

    Aditivo, não-multiplicativo: `effective_fee_bps = baseline + fee_delta_bps`.
    Sempre não-negativo — stress aumenta custo contra o trader; reduzir custo
    é análise paralela que, se precisar, vira ADR.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    label: str = Field(min_length=1)
    fee_delta_bps: float = Field(ge=0.0)
    slip_delta_bps: float = Field(ge=0.0)
    spread_delta_bps: float = Field(ge=0.0, default=0.0)


class CostStressCell(BaseModel):
    """Uma linha do `CostStressReport`: um cenário rodado (ADR-0014).

    `scenario_index=0` é o baseline; `scenario_index ≥ 1` são as perturbações
    na ordem da lista passada a `cost_stress`.
    `final_equity_delta_vs_baseline <= tolerance` por ADR-0010 (monotonicidade
    de custo); o próprio `cost_stress` assert-a isso antes de devolver.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    scenario_index: int = Field(ge=0)
    label: str = Field(min_length=1)
    cost: CostModel
    result: BacktestResult
    final_equity: float
    final_equity_delta_vs_baseline: float


class CostStressReport(BaseModel):
    """Resultado de um `cost_stress`: baseline + N cenários perturbados (ADR-0014)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_id: str = Field(min_length=1)
    baseline: CostStressCell
    scenarios: list[CostStressCell] = Field(min_length=1)


class RunMetadata(BaseModel):
    """Metadados de uma corrida da CLI `validate` (ADR-0017).

    Persiste versão, timestamp UTC, comando, run_id e flags — `flags` é
    `dict[str, str]` para estabilidade de schema (Union heterogêneo rejeitado
    na ADR-0017 §"Alternatives").
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    alpha_forge_version: str = Field(min_length=1)
    timestamp_utc: datetime
    command: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    flags: dict[str, str]
