"""Ranking module (ADR-0024) — ordena pilotos validados por composite score."""
from alpha_forge.ranking.scoring import (
    DEFAULT_WEIGHTS,
    LeaderboardRow,
    RankedLeaderboard,
    RankingError,
    ScoreWeights,
    discover_slugs,
    load_weights_toml,
    rank_pilots,
    save_leaderboard,
)

__all__ = [
    "DEFAULT_WEIGHTS",
    "LeaderboardRow",
    "RankedLeaderboard",
    "RankingError",
    "ScoreWeights",
    "discover_slugs",
    "load_weights_toml",
    "rank_pilots",
    "save_leaderboard",
]
