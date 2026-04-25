"""Validação: walk-forward causal + Monte Carlo sobre trades + stress de custos + persistência + metadados (ADR-0003, ADR-0014, ADR-0015, ADR-0017)."""

from alpha_forge.validation.cost_stress import cost_stress
from alpha_forge.validation.monte_carlo import monte_carlo_trades
from alpha_forge.validation.persistence import (
    load_cost_stress_report,
    load_monte_carlo_summary,
    load_run_metadata,
    load_walk_forward_folds,
    save_cost_stress_report,
    save_monte_carlo_summary,
    save_run_metadata,
    save_walk_forward_folds,
)
from alpha_forge.validation.schemas import (
    CostPerturbation,
    CostStressCell,
    CostStressReport,
    MonteCarloSummary,
    RunMetadata,
    WalkForwardFold,
    WalkForwardWindow,
)
from alpha_forge.validation.walk_forward import ValidationError, walk_forward

__all__ = [
    "CostPerturbation",
    "CostStressCell",
    "CostStressReport",
    "MonteCarloSummary",
    "RunMetadata",
    "ValidationError",
    "WalkForwardFold",
    "WalkForwardWindow",
    "cost_stress",
    "load_cost_stress_report",
    "load_monte_carlo_summary",
    "load_run_metadata",
    "load_walk_forward_folds",
    "monte_carlo_trades",
    "save_cost_stress_report",
    "save_monte_carlo_summary",
    "save_run_metadata",
    "save_walk_forward_folds",
    "walk_forward",
]
