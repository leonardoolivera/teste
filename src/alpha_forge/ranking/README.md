# `ranking/` — módulo 7

## Responsabilidade

Calcular métricas finais, score multiobjetivo e saídas comparativas. Duas subáreas internas declaradas:

- **`scoring/`** — métricas + score multiobjetivo + leaderboard.
- **`reporting/`** — relatórios comparativos + export.

Separação interna deliberada; extração em módulos próprios só se crescer (ADR-0001).

## O que ainda não existe

Tudo. Nem métricas, nem score, nem relatórios.

Capabilities previstas em `vision/02-scope.md`:

- métricas (retorno, drawdown, Sharpe, Sortino, Calmar, profit factor, expectancy, hit rate, ulcer index, exposure time, turnover, risco de ruína aproximado, robustness por regime)
- score multiobjetivo com pesos configuráveis
- leaderboard
- comparação entre estratégias
- relatórios comparativos
- exportação de resultados

## Depende de

`validation`, `regimes`.

## Primeiro arquivo real esperado

`scoring/schemas.py` — `Metric` (enum), `MetricValue`, `ScoreWeights` (pesos configuráveis), `StrategyScore`. Segundo passo: `scoring/metrics.py` (cálculos individuais) e `scoring/multiobjective.py` (agregação).

Referência: ADR-0006 (scoring multiobjetivo, a escrever).
