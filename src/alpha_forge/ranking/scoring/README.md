# `ranking/scoring/` — subárea de scoring

## Responsabilidade

Cálculo de métricas individuais, agregação multiobjetivo com pesos configuráveis e leaderboard.

## O que ainda não existe

Tudo.

## Depende de

`validation`.

## Primeiro arquivo real esperado

`schemas.py` (tipos) → `metrics.py` (cálculos individuais) → `multiobjective.py` (agregação) → `leaderboard.py` (ordenação por score).
