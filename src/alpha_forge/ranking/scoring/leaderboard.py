"""Leaderboard determinístico sobre pilotos validados (ADR-0024).

Consome `results/validation/<slug>/{run,walk_forward,monte_carlo,cost_stress}.json`
via loaders de `validation/persistence.py`. Produz `RankedLeaderboard` imutável
via score linear ponderado com normalização min-max.

Invariantes estão em `tests/ranking/test_leaderboard_properties.py` (property-based).
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

import alpha_forge
from alpha_forge.ranking.scoring.schemas import (
    DEFAULT_WEIGHTS,
    LeaderboardRow,
    RankedLeaderboard,
    ReleaseDecision,
    ScoreWeights,
)
from alpha_forge.validation.persistence import (
    load_cost_stress_report,
    load_monte_carlo_summary,
    load_run_metadata,
    load_walk_forward_folds,
)

_SPREAD_STRESS_LABEL = "spread+10"
_RELEASE_DECISION_RE = re.compile(
    r"^release_decision\s*:\s*\*{0,2}`?(fail|paper_only|canary_only)`?\*{0,2}",
    re.IGNORECASE | re.MULTILINE,
)


class RankingError(Exception):
    """Erro fatal do ranking (ex: nenhum piloto elegível)."""


# --------------------------------------------------------------------------- #
# Parse helpers
# --------------------------------------------------------------------------- #


def _parse_release_decision(audit_path: Path) -> ReleaseDecision:
    text = audit_path.read_text(encoding="utf-8")
    match = _RELEASE_DECISION_RE.search(text)
    if not match:
        raise RankingError(
            f"não encontrei 'release_decision: <fail|paper_only|canary_only>' em {audit_path}"
        )
    return match.group(1).lower()  # type: ignore[return-value]


def _flags_digest(flags: dict[str, str]) -> str:
    canonical = json.dumps(flags, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


# --------------------------------------------------------------------------- #
# Row extraction
# --------------------------------------------------------------------------- #


def _extract_row_raw(
    slug: str,
    runs_dir: Path,
    agentic_dir: Path | None,
) -> dict[str, float | int | str]:
    """Carrega os 4 JSONs + AUDIT.md e devolve os campos brutos do piloto.

    Não aplica rank nem composite_score — isso vem depois, sobre a amostra inteira.
    """
    pilot_dir = runs_dir / slug
    run = load_run_metadata(directory=pilot_dir)
    wf_folds = load_walk_forward_folds(directory=pilot_dir)
    mc = load_monte_carlo_summary(directory=pilot_dir)
    cs = load_cost_stress_report(directory=pilot_dir)

    baseline_fe = cs.baseline.final_equity
    baseline_metrics = cs.baseline.result.metrics
    if baseline_metrics is None:
        raise RankingError(f"{slug}: cost_stress baseline sem metrics")
    hit_baseline = baseline_metrics.hit_rate
    if hit_baseline is None:
        raise RankingError(f"{slug}: hit_rate baseline ausente (trade_count=0?)")

    spread_cell = next(
        (s for s in cs.scenarios if s.label == _SPREAD_STRESS_LABEL), None
    )
    if spread_cell is None:
        raise RankingError(
            f"{slug}: cost_stress não contém cenário '{_SPREAD_STRESS_LABEL}' — necessário para spread_stress_ratio (ADR-0024)"
        )
    if baseline_fe == 0:
        raise RankingError(f"{slug}: baseline final_equity é zero")
    spread_stress_ratio = spread_cell.final_equity / baseline_fe

    fold_hits: list[float] = []
    for fold in wf_folds:
        m = fold.result.metrics
        if m is None or m.hit_rate is None:
            continue
        fold_hits.append(m.hit_rate)
    if not fold_hits:
        raise RankingError(f"{slug}: nenhum fold com hit_rate válido")

    # pstdev com n=1 → 0. Garante fold_std_hit >=0 sempre.
    fold_std = statistics.pstdev(fold_hits) if len(fold_hits) > 1 else 0.0

    if agentic_dir is None:
        agentic_dir = runs_dir.parents[1] / "agentic" / "active"
    audit_path = agentic_dir / slug / "AUDIT.md"
    release_decision: ReleaseDecision
    if audit_path.exists():
        release_decision = _parse_release_decision(audit_path)
    else:
        # Sem AUDIT.md o piloto tecnicamente não completou o gate — tratamos como
        # 'fail' para não bloquear ranking de séries experimentais ainda em curso.
        release_decision = "fail"

    return {
        "slug": slug,
        "fe_baseline": baseline_fe,
        "hit_baseline": hit_baseline,
        "mdd_baseline": baseline_metrics.max_drawdown,
        "trade_count": baseline_metrics.trade_count,
        "spread_stress_ratio": spread_stress_ratio,
        "mc_p5": mc.final_equity_percentiles[5],
        "mc_p50": mc.final_equity_percentiles[50],
        "mc_p95": mc.final_equity_percentiles[95],
        "fold_max_hit": max(fold_hits),
        "fold_min_hit": min(fold_hits),
        "fold_std_hit": fold_std,
        "release_decision": release_decision,
        "flags_digest": _flags_digest(run.flags),
    }


# --------------------------------------------------------------------------- #
# Normalization + score
# --------------------------------------------------------------------------- #


def _minmax(values: list[float], *, higher_better: bool) -> list[float]:
    """Normaliza para [0,1]. Se todos iguais → 0.5 (documentado em ADR-0024)."""
    lo = min(values)
    hi = max(values)
    if math.isclose(lo, hi):
        return [0.5] * len(values)
    rng = hi - lo
    if higher_better:
        return [(v - lo) / rng for v in values]
    return [(hi - v) / rng for v in values]


def _compute_composite_scores(
    raw_rows: list[dict[str, float | int | str]],
    weights: ScoreWeights,
) -> list[float]:
    fe = _minmax([float(r["fe_baseline"]) for r in raw_rows], higher_better=True)
    hit = _minmax([float(r["hit_baseline"]) for r in raw_rows], higher_better=True)
    mdd = _minmax([float(r["mdd_baseline"]) for r in raw_rows], higher_better=False)
    stress = _minmax(
        [float(r["spread_stress_ratio"]) for r in raw_rows], higher_better=True
    )
    p5 = _minmax([float(r["mc_p5"]) for r in raw_rows], higher_better=True)
    fold_min = _minmax(
        [float(r["fold_min_hit"]) for r in raw_rows], higher_better=True
    )
    fold_std = _minmax(
        [float(r["fold_std_hit"]) for r in raw_rows], higher_better=False
    )

    scores: list[float] = []
    for i in range(len(raw_rows)):
        s = (
            weights.w_fe * fe[i]
            + weights.w_hit * hit[i]
            + weights.w_mdd * mdd[i]
            + weights.w_stress * stress[i]
            + weights.w_p5 * p5[i]
            + weights.w_fold_min * fold_min[i]
            + weights.w_fold_std * fold_std[i]
        )
        scores.append(s)
    return scores


# --------------------------------------------------------------------------- #
# Eligibility mini-DSL
# --------------------------------------------------------------------------- #


_ELIG_RE = re.compile(
    r"^\s*release_decision\s*(==|!=)\s*['\"](fail|paper_only|canary_only)['\"]\s*$"
)


def _build_eligibility(expr: str) -> Callable[[dict[str, float | int | str]], bool]:
    if expr == "all":
        return lambda _row: True
    m = _ELIG_RE.match(expr)
    if not m:
        raise RankingError(
            f"eligibility inválida: {expr!r}. v1 aceita apenas "
            "'all' ou \"release_decision (==|!=) 'fail|paper_only|canary_only'\" (ADR-0024)."
        )
    op, value = m.group(1), m.group(2)
    if op == "==":
        return lambda row: row["release_decision"] == value
    return lambda row: row["release_decision"] != value


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def discover_slugs(runs_dir: Path) -> list[str]:
    """Retorna subdiretórios que têm os 4 JSONs canônicos, ordenados lex."""
    slugs: list[str] = []
    if not runs_dir.exists():
        return slugs
    for child in sorted(runs_dir.iterdir()):
        if not child.is_dir():
            continue
        if all(
            (child / f).exists()
            for f in ("run.json", "walk_forward.json", "monte_carlo.json", "cost_stress.json")
        ):
            slugs.append(child.name)
    return slugs


def rank_pilots(
    *,
    slugs: Iterable[str],
    runs_dir: Path,
    weights: ScoreWeights | None = None,
    eligibility: str = "all",
    agentic_dir: Path | None = None,
    warn_stream: object = sys.stderr,
    generated_at: str | None = None,
) -> RankedLeaderboard:
    """Ordena os pilotos em `slugs` por composite score (ADR-0024).

    Pilotos com artefatos ausentes/inconsistentes são pulados com warning em
    `warn_stream`. Raises `RankingError` apenas se zero pilotos sobrevivem.
    """
    effective_weights = weights or ScoreWeights()
    filter_fn = _build_eligibility(eligibility)

    raw_rows: list[dict[str, float | int | str]] = []
    for slug in sorted(set(slugs)):
        try:
            row = _extract_row_raw(slug, runs_dir, agentic_dir)
        except (RankingError, FileNotFoundError, ValueError) as exc:
            print(f"[rank] aviso: pulando {slug!r}: {exc}", file=warn_stream)
            continue
        if filter_fn(row):
            raw_rows.append(row)

    if not raw_rows:
        raise RankingError(
            "zero pilotos elegíveis após eligibility + filtragem de artefatos ausentes"
        )

    scores = _compute_composite_scores(raw_rows, effective_weights)

    indexed = list(zip(raw_rows, scores, strict=True))
    # Ordena score desc, tiebreak slug asc.
    indexed.sort(key=lambda pair: (-pair[1], pair[0]["slug"]))

    rows: list[LeaderboardRow] = []
    for i, (raw, score) in enumerate(indexed, start=1):
        rows.append(
            LeaderboardRow(
                rank=i,
                slug=str(raw["slug"]),
                fe_baseline=float(raw["fe_baseline"]),
                hit_baseline=float(raw["hit_baseline"]),
                mdd_baseline=float(raw["mdd_baseline"]),
                trade_count=int(raw["trade_count"]),
                spread_stress_ratio=float(raw["spread_stress_ratio"]),
                mc_p5=float(raw["mc_p5"]),
                mc_p50=float(raw["mc_p50"]),
                mc_p95=float(raw["mc_p95"]),
                fold_max_hit=float(raw["fold_max_hit"]),
                fold_min_hit=float(raw["fold_min_hit"]),
                fold_std_hit=float(raw["fold_std_hit"]),
                release_decision=str(raw["release_decision"]),  # type: ignore[arg-type]
                composite_score=score,
                flags_digest=str(raw["flags_digest"]),
            )
        )

    ts = generated_at if generated_at is not None else datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    return RankedLeaderboard(
        generated_at=ts,
        alpha_forge_version=alpha_forge.__version__,
        weights=effective_weights.as_dict(),
        eligibility=eligibility,
        rows=rows,
    )


# --------------------------------------------------------------------------- #
# Weights from TOML
# --------------------------------------------------------------------------- #


def load_weights_toml(path: Path) -> ScoreWeights:
    """Carrega um arquivo TOML com [weights] e retorna um `ScoreWeights`.

    Chaves ausentes caem para o default documentado em ADR-0024.
    """
    import tomllib

    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    section = raw.get("weights", {})
    if not isinstance(section, dict):
        raise RankingError(f"{path}: seção [weights] ausente ou inválida")
    merged = dict(DEFAULT_WEIGHTS)
    for k, v in section.items():
        if k not in merged:
            raise RankingError(f"{path}: peso desconhecido {k!r} em [weights]")
        if not isinstance(v, (int, float)):
            raise RankingError(f"{path}: peso {k!r} não-numérico")
        merged[k] = float(v)
    return ScoreWeights(**merged)


def save_leaderboard(leaderboard: RankedLeaderboard, path: Path) -> Path:
    """Grava o leaderboard como JSON simples (sem envelope — output de usuário)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(leaderboard.model_dump(mode="json"), indent=2), encoding="utf-8"
    )
    return path
