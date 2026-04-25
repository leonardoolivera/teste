# `ranking/` — módulo 7

## Responsabilidade

Ordenar pilotos já validados por composite score (ADR-0024). Duas subáreas internas declaradas:

- **`scoring/`** — schemas (`LeaderboardRow`, `RankedLeaderboard`, `ScoreWeights`) + leaderboard determinístico (`rank_pilots`, `discover_slugs`, `load_weights_toml`, `save_leaderboard`).
- **`reporting/`** — relatórios comparativos e exports. **Ainda vazio** — TBD até haver consumidor concreto (candidato: `rank-diff` entre dois leaderboards; exports markdown).

Separação interna deliberada; extração em módulos próprios só se crescer (ADR-0001).

## O que existe (ADR-0024, 2026-04-18)

- `scoring/schemas.py` — `ScoreWeights`, `LeaderboardRow`, `RankedLeaderboard`, `DEFAULT_WEIGHTS`. Todos frozen + `extra="forbid"`.
- `scoring/leaderboard.py` — `rank_pilots(...)` (score linear ponderado com min-max normalização, tiebreak slug asc), `discover_slugs`, `load_weights_toml`, `save_leaderboard`, `RankingError`.
- CLI: `alpha-forge rank [--runs-dir ...] [--slug ...]* [--weights-file ...] [--eligibility ...] [--output ...] [--format json|table]`.
- 7 testes em `tests/property/test_ranking_properties.py` + 1 integration em `tests/integration/test_cli_rank.py`.

## O que ainda não existe

- `reporting/` inteiro.
- Scoring Pareto-dominance (v2 candidato se o linear ponderado mostrar patologias — ADR-0024 §"Alternatives").
- Outras métricas previstas em `vision/02-scope.md` (Sharpe, Sortino, Calmar, profit factor, expectancy, ulcer, exposure time, turnover, risco de ruína aproximado, robustness por regime). Adicionar no score composto exige superseding ADR-0024.

## Depende de

- `validation/persistence.py` — loaders de `walk_forward.json`, `monte_carlo.json`, `cost_stress.json`, `run.json`.
- `validation/schemas.py` — `WalkForwardFold`, `MonteCarloSummary`, `CostStressReport`, `RunMetadata`.
- Externos: `pydantic`, `tomllib` (stdlib desde Python 3.11), `statistics` (stdlib).

## Referências

- ADR-0024 — contrato formal do ranking, score composto v1, CLI.
- ADR-0015 / ADR-0017 — formato dos artefatos JSON consumidos.
- ADR-0019 — definição do cenário `spread+10` usado em `spread_stress_ratio`.
