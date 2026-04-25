"""Contratos do módulo de ranking (ADR-0024).

Tudo frozen + `extra="forbid"` — mesma rigidez dos contratos de `validation/`.
Pesos default documentados na própria ADR; alterar aqui exige superseding ADR.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ReleaseDecision = Literal["fail", "paper_only", "canary_only"]

# Default weights documentados em ADR-0024 §Score composto v1.
DEFAULT_WEIGHTS: dict[str, float] = {
    "w_fe": 1.0,
    "w_hit": 2.0,
    "w_mdd": 1.5,
    "w_stress": 1.0,
    "w_p5": 1.5,
    "w_fold_min": 1.0,
    "w_fold_std": 0.5,
}


class ScoreWeights(BaseModel):
    """Pesos para o score linear ponderado (ADR-0024)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    w_fe: float = DEFAULT_WEIGHTS["w_fe"]
    w_hit: float = DEFAULT_WEIGHTS["w_hit"]
    w_mdd: float = DEFAULT_WEIGHTS["w_mdd"]
    w_stress: float = DEFAULT_WEIGHTS["w_stress"]
    w_p5: float = DEFAULT_WEIGHTS["w_p5"]
    w_fold_min: float = DEFAULT_WEIGHTS["w_fold_min"]
    w_fold_std: float = DEFAULT_WEIGHTS["w_fold_std"]

    def as_dict(self) -> dict[str, float]:
        return {
            "w_fe": self.w_fe,
            "w_hit": self.w_hit,
            "w_mdd": self.w_mdd,
            "w_stress": self.w_stress,
            "w_p5": self.w_p5,
            "w_fold_min": self.w_fold_min,
            "w_fold_std": self.w_fold_std,
        }


class LeaderboardRow(BaseModel):
    """Uma linha do ranking (ADR-0024)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rank: int = Field(ge=1)
    slug: str = Field(min_length=1)
    fe_baseline: float
    hit_baseline: float = Field(ge=0.0, le=1.0)
    mdd_baseline: float = Field(ge=0.0, le=1.0)
    trade_count: int = Field(ge=0)
    spread_stress_ratio: float
    mc_p5: float
    mc_p50: float
    mc_p95: float
    fold_max_hit: float = Field(ge=0.0, le=1.0)
    fold_min_hit: float = Field(ge=0.0, le=1.0)
    fold_std_hit: float = Field(ge=0.0)
    release_decision: ReleaseDecision
    composite_score: float
    flags_digest: str = Field(min_length=16, max_length=16)


class RankedLeaderboard(BaseModel):
    """Leaderboard completo (ADR-0024). Output de `rank_pilots`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    generated_at: str = Field(min_length=1)
    alpha_forge_version: str = Field(min_length=1)
    weights: dict[str, float]
    eligibility: str = Field(min_length=1)
    rows: list[LeaderboardRow]
