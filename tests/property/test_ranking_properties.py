"""Property-based para `rank_pilots` (ADR-0024).

5 invariantes obrigatórios:
1. Permutação-invariância do input não altera a ordem de saída.
2. Min-max constante → score constante (todos os pilotos iguais → todos 0.5).
3. Determinismo bit-a-bit (modulo `generated_at`).
4. `flags_digest` estável: mesma config → mesmo digest; config diferente → digest diferente.
5. Eligibility filtra sem reordenar os sobreviventes.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from alpha_forge.ranking import (
    RankingError,
    ScoreWeights,
    rank_pilots,
)
from alpha_forge.ranking.scoring.leaderboard import _flags_digest


SCHEMA_VERSION = "1"


def _write_piloto(
    dir_: Path,
    *,
    slug: str,
    fe_baseline: float,
    hit: float,
    mdd: float,
    trade_count: int,
    spread_fe: float,
    mc: dict[int, float],
    fold_hits: list[float],
    release_decision: str = "fail",
    flags: dict[str, str] | None = None,
    agentic_dir: Path | None = None,
) -> None:
    """Cria um diretório `dir_/<slug>/` com os 4 JSONs canônicos + AUDIT.md."""
    pilot = dir_ / slug
    pilot.mkdir(parents=True, exist_ok=True)

    # run.json
    flags = flags or {"dataset_id": "synthetic", "run_id": slug}
    run = {
        "alpha_forge_version": "0.0.0",
        "timestamp_utc": "2026-04-18T00:00:00Z",
        "command": "validate",
        "run_id": slug,
        "flags": flags,
    }
    (pilot / "run.json").write_text(
        json.dumps({"schema_version": SCHEMA_VERSION, "payload": run}),
        encoding="utf-8",
    )

    # walk_forward.json
    wf_payload = []
    for i, h in enumerate(fold_hits, start=1):
        wf_payload.append(
            {
                "fold_index": i,
                "train_window": {
                    "start": "2024-01-01T00:00:00Z",
                    "end": "2024-02-01T00:00:00Z",
                    "bars": 100,
                },
                "test_window": {
                    "start": "2024-02-01T00:00:00Z",
                    "end": "2024-03-01T00:00:00Z",
                    "bars": 100,
                },
                "result": _fake_result(
                    hit=h, fe=fe_baseline, mdd=mdd, trade_count=trade_count
                ),
            }
        )
    (pilot / "walk_forward.json").write_text(
        json.dumps({"schema_version": SCHEMA_VERSION, "payload": wf_payload}),
        encoding="utf-8",
    )

    # monte_carlo.json
    mc_payload = {
        "n_resamples": 500,
        "seed": 42,
        "final_equity_percentiles": {str(k): v for k, v in mc.items()},
        "max_drawdown_percentiles": {
            "5": 0.01, "25": 0.02, "50": 0.03, "75": 0.04, "95": 0.05
        },
        "original_final_equity": fe_baseline,
        "original_max_drawdown": mdd,
    }
    (pilot / "monte_carlo.json").write_text(
        json.dumps({"schema_version": SCHEMA_VERSION, "payload": mc_payload}),
        encoding="utf-8",
    )

    # cost_stress.json
    cs_payload = {
        "dataset_id": "synthetic",
        "baseline": _fake_cost_cell(
            0, "baseline", fe_baseline, hit, mdd, trade_count, delta=0.0,
            fee_bps=5.0, slip_bps=2.0, spread_bps=0.0,
        ),
        "scenarios": [
            _fake_cost_cell(
                1, "spread+10", spread_fe, hit, mdd, trade_count,
                delta=spread_fe - fe_baseline,
                fee_bps=5.0, slip_bps=2.0, spread_bps=10.0,
            ),
        ],
    }
    (pilot / "cost_stress.json").write_text(
        json.dumps({"schema_version": SCHEMA_VERSION, "payload": cs_payload}),
        encoding="utf-8",
    )

    if agentic_dir is not None:
        adir = agentic_dir / slug
        adir.mkdir(parents=True, exist_ok=True)
        (adir / "AUDIT.md").write_text(
            f"# AUDIT — {slug}\n\nrelease_decision: {release_decision}\n",
            encoding="utf-8",
        )


def _fake_result(*, hit: float, fe: float, mdd: float, trade_count: int) -> dict:
    return {
        "dataset_id": "synthetic",
        "bars": 100,
        "fills": [],
        "rejections": [],
        "trades": [],
        "final_equity": fe,
        "max_equity": fe,
        "min_equity": fe,
        "equity_curve": [],
        "metrics": {
            "total_pnl": fe - 10000.0,
            "trade_count": trade_count,
            "hit_rate": hit,
            "max_drawdown": mdd,
        },
    }


def _fake_cost_cell(
    scenario_index: int,
    label: str,
    fe: float,
    hit: float,
    mdd: float,
    trade_count: int,
    *,
    delta: float,
    fee_bps: float,
    slip_bps: float,
    spread_bps: float,
) -> dict:
    return {
        "scenario_index": scenario_index,
        "label": label,
        "cost": {
            "taker_fee_bps": fee_bps,
            "slippage_bps_per_unit_notional": slip_bps,
            "spread_bps": spread_bps,
        },
        "result": _fake_result(hit=hit, fe=fe, mdd=mdd, trade_count=trade_count),
        "final_equity": fe,
        "final_equity_delta_vs_baseline": delta,
    }


@pytest.fixture
def sample_runs(tmp_path: Path) -> tuple[Path, Path, list[str]]:
    runs = tmp_path / "runs"
    agentic = tmp_path / "agentic"
    slugs = ["alpha", "bravo", "charlie", "delta"]
    configs = [
        ("alpha", 9000.0, 0.25, 0.10, 100, 8700.0, [0.2, 0.3, 0.25, 0.22]),
        ("bravo", 10500.0, 0.32, 0.06, 90, 10300.0, [0.3, 0.35, 0.33, 0.30]),
        ("charlie", 9500.0, 0.30, 0.08, 150, 9100.0, [0.25, 0.31, 0.28, 0.35]),
        ("delta", 8500.0, 0.27, 0.15, 220, 8200.0, [0.22, 0.30, 0.26, 0.24]),
    ]
    for slug, fe, hit, mdd, tc, sfe, folds in configs:
        _write_piloto(
            runs,
            slug=slug,
            fe_baseline=fe,
            hit=hit,
            mdd=mdd,
            trade_count=tc,
            spread_fe=sfe,
            mc={5: fe * 0.93, 25: fe * 0.97, 50: fe, 75: fe * 1.03, 95: fe * 1.07},
            fold_hits=folds,
            agentic_dir=agentic,
        )
    return runs, agentic, slugs


# --------------------------------------------------------------------------- #
# 1. Permutação-invariância
# --------------------------------------------------------------------------- #


@given(seed=st.integers(min_value=0, max_value=10_000))
@settings(max_examples=15, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_permutation_invariance(sample_runs: tuple[Path, Path, list[str]], seed: int) -> None:
    import random
    runs, agentic, slugs = sample_runs
    r = random.Random(seed)
    permuted = slugs[:]
    r.shuffle(permuted)

    lb_a = rank_pilots(
        slugs=slugs,
        runs_dir=runs,
        agentic_dir=agentic,
        generated_at="2026-01-01T00:00:00Z",
    )
    lb_b = rank_pilots(
        slugs=permuted,
        runs_dir=runs,
        agentic_dir=agentic,
        generated_at="2026-01-01T00:00:00Z",
    )
    order_a = [(r.slug, r.rank) for r in lb_a.rows]
    order_b = [(r.slug, r.rank) for r in lb_b.rows]
    assert order_a == order_b


# --------------------------------------------------------------------------- #
# 2. Min-max constante
# --------------------------------------------------------------------------- #


def test_all_equal_pilots_get_equal_scores(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    agentic = tmp_path / "agentic"
    for slug in ("a", "b", "c"):
        _write_piloto(
            runs,
            slug=slug,
            fe_baseline=9000.0,
            hit=0.3,
            mdd=0.1,
            trade_count=100,
            spread_fe=8800.0,
            mc={5: 8500.0, 25: 8800.0, 50: 9000.0, 75: 9200.0, 95: 9500.0},
            fold_hits=[0.25, 0.30, 0.28],
            agentic_dir=agentic,
        )
    lb = rank_pilots(
        slugs=["a", "b", "c"],
        runs_dir=runs,
        agentic_dir=agentic,
        generated_at="2026-01-01T00:00:00Z",
    )
    scores = {r.composite_score for r in lb.rows}
    assert len(scores) == 1  # todos idênticos
    # Score = soma dos pesos * 0.5
    w = ScoreWeights()
    expected = sum(w.as_dict().values()) * 0.5
    assert abs(lb.rows[0].composite_score - expected) < 1e-9


# --------------------------------------------------------------------------- #
# 3. Determinismo bit-a-bit
# --------------------------------------------------------------------------- #


def test_determinism_bit_exact(sample_runs: tuple[Path, Path, list[str]]) -> None:
    runs, agentic, slugs = sample_runs
    lb1 = rank_pilots(
        slugs=slugs, runs_dir=runs, agentic_dir=agentic,
        generated_at="2026-01-01T00:00:00Z",
    )
    lb2 = rank_pilots(
        slugs=slugs, runs_dir=runs, agentic_dir=agentic,
        generated_at="2026-01-01T00:00:00Z",
    )
    assert lb1.model_dump_json() == lb2.model_dump_json()


# --------------------------------------------------------------------------- #
# 4. flags_digest estável
# --------------------------------------------------------------------------- #


def test_flags_digest_stable_and_sensitive() -> None:
    a = {"run_id": "x", "dataset_id": "btc", "capital": "10000"}
    b = {"capital": "10000", "dataset_id": "btc", "run_id": "x"}  # ordem diferente
    c = {"run_id": "x", "dataset_id": "btc", "capital": "10001"}  # valor diferente
    assert _flags_digest(a) == _flags_digest(b)
    assert _flags_digest(a) != _flags_digest(c)
    assert len(_flags_digest(a)) == 16


# --------------------------------------------------------------------------- #
# 5. Eligibility filtra sem reordenar
# --------------------------------------------------------------------------- #


def test_eligibility_filters_without_reordering(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    agentic = tmp_path / "agentic"
    # 3 pilotos: alpha fail, bravo paper_only, charlie fail
    configs = [
        ("alpha", 9000.0, 0.25, "fail"),
        ("bravo", 10500.0, 0.32, "paper_only"),
        ("charlie", 9500.0, 0.30, "fail"),
    ]
    for slug, fe, hit, decision in configs:
        _write_piloto(
            runs,
            slug=slug,
            fe_baseline=fe,
            hit=hit,
            mdd=0.1,
            trade_count=100,
            spread_fe=fe * 0.97,
            mc={5: fe * 0.93, 25: fe * 0.97, 50: fe, 75: fe * 1.03, 95: fe * 1.07},
            fold_hits=[hit - 0.02, hit, hit + 0.02, hit - 0.01],
            release_decision=decision,
            agentic_dir=agentic,
        )
    full = rank_pilots(
        slugs=["alpha", "bravo", "charlie"],
        runs_dir=runs, agentic_dir=agentic,
        generated_at="2026-01-01T00:00:00Z",
    )
    filtered = rank_pilots(
        slugs=["alpha", "bravo", "charlie"],
        runs_dir=runs, agentic_dir=agentic,
        eligibility="release_decision != 'fail'",
        generated_at="2026-01-01T00:00:00Z",
    )
    full_order = [r.slug for r in full.rows]
    filtered_order = [r.slug for r in filtered.rows]
    # Filtered deve ser subset de full preservando ordem relativa
    assert filtered_order == [s for s in full_order if s == "bravo"]
    assert all(r.release_decision == "paper_only" for r in filtered.rows)


def test_zero_eligible_raises(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    agentic = tmp_path / "agentic"
    _write_piloto(
        runs, slug="a", fe_baseline=9000.0, hit=0.25, mdd=0.1, trade_count=100,
        spread_fe=8700.0,
        mc={5: 8500.0, 25: 8800.0, 50: 9000.0, 75: 9200.0, 95: 9500.0},
        fold_hits=[0.2, 0.3], agentic_dir=agentic,
    )
    with pytest.raises(RankingError):
        rank_pilots(
            slugs=["a"], runs_dir=runs, agentic_dir=agentic,
            eligibility="release_decision != 'fail'",
        )
