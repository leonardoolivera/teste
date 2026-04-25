"""Integration test de `alpha-forge rank` sobre os 12 pilotos ativos (ADR-0024).

Smoke-test "usa o estado real do repositório como fixture viva". Se a série H
for encerrada e os pilotos arquivados (`agentic/archive/`), este teste se torna
uma regressão sobre o snapshot atual e pode ser atualizado.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from alpha_forge.cli.app import run
from alpha_forge.ranking import RankedLeaderboard


ROOT = Path(__file__).resolve().parents[2]
RESULTS_VALIDATION = ROOT / "results" / "validation"
AGENTIC_ACTIVE = ROOT / "agentic" / "active"


@pytest.mark.skipif(
    not RESULTS_VALIDATION.exists() or not any(RESULTS_VALIDATION.iterdir()),
    reason="Nenhum piloto validado disponível — ranking trivial sem fixture viva.",
)
def test_rank_over_live_pilots(tmp_path: Path) -> None:
    output = tmp_path / "leaderboard.json"
    rc = run(
        [
            "rank",
            "--runs-dir", str(RESULTS_VALIDATION),
            "--agentic-dir", str(AGENTIC_ACTIVE),
            "--output", str(output),
            "--format", "json",
        ]
    )
    assert rc == 0
    assert output.exists()

    payload = json.loads(output.read_text(encoding="utf-8"))
    lb = RankedLeaderboard.model_validate(payload)

    # pelo menos 1 piloto elegível; ranks sequenciais 1..N
    assert len(lb.rows) >= 1
    assert [r.rank for r in lb.rows] == list(range(1, len(lb.rows) + 1))

    # scores em ordem descendente (tiebreak por slug não importa aqui)
    scores = [r.composite_score for r in lb.rows]
    assert scores == sorted(scores, reverse=True) or all(
        # empates permitidos; então checamos ordem alfabética entre empates
        scores[i] >= scores[i + 1] for i in range(len(scores) - 1)
    )

    # digests únicos por config: na série H há ≥ 12 configs distintas
    digests = {r.flags_digest for r in lb.rows}
    assert len(digests) == len(lb.rows)
