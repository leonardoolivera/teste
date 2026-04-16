# 0007 — Minimal backtest metrics

**Status:** Accepted
**Date:** 2026-04-16
**Deciders:** Usuário (owner do projeto) + agente.

## Context

O núcleo mínimo produz hoje apenas `final_equity`, `max_equity`, `min_equity`, `equity_curve`, contagens de fills e rejections. Sem número de trades fechados, hit rate ou drawdown, é impossível caracterizar uma estratégia de forma mínima ou comparar a dummy com a primeira estratégia séria (moving average crossover causal, próximo passo).

ADR-0006 estabeleceu o modelo de custos antes das métricas justamente para que as métricas nascessem sobre resultado com atrito. Esta ADR fixa o conjunto mínimo, onde ele vive e como trata casos degenerados.

Não é sistema de scoring multiobjetivo. Isso é `ranking/scoring/` e vira ADR própria quando houver comparação entre estratégias.

## Decision

O núcleo expõe exatamente **quatro métricas** a partir de um `BacktestResult`:

1. **`total_pnl: float`** — `final_equity - capital_inicial`. Em unidades absolutas de capital (não percentual).
2. **`trade_count: int`** — número de trades fechados (um "trade" = par entrada-saída; entrada sem saída correspondente até o fim do backtest **não conta**).
3. **`hit_rate: float | None`** — fração de trades fechados com PnL > 0. `None` quando `trade_count == 0`. Semântica explícita: não retorna `0.0` nem `NaN` em ausência de trades — retorna `None` para que o consumidor decida como representar "indefinido".
4. **`max_drawdown: float`** — maior queda percentual da curva de equity desde o pico anterior, em valor não negativo (`0.0` a `1.0`). Calculada via `(1 - equity / running_max).max()`. Uma curva estritamente não-decrescente devolve `0.0`.

Agrupadas em um único objeto `BacktestMetrics` (pydantic v2, frozen), computado por função pura `compute_metrics(result: BacktestResult, capital_inicial: float) -> BacktestMetrics`.

**Onde vive:** `src/alpha_forge/backtest/metrics.py`. Decisão consciente de manter em `backtest/` por enquanto, e **não** em `ranking/scoring/`. Motivo: enquanto o escopo for "caracterizar um backtest", a métrica é parte do backtest. Quando houver comparação multi-estratégia, `ranking/scoring/` herda ou agrega essas métricas — ADR futura.

**Comportamento explícito em casos degenerados:**

- **Zero trades fechados** (`trade_count == 0`): `total_pnl = 0.0` (ou o que for a variação mark-to-market final, que com posição nunca aberta é zero), `hit_rate = None`, `max_drawdown = 0.0`.
- **Equity flat** (sem oscilação): `max_drawdown = 0.0`, `total_pnl = 0.0`.
- **Backtest com só 1 barra** (já rejeitado pelo engine com `ValueError`): irrelevante aqui.
- **Trade aberto ao fim do backtest** (entrada sem saída): ignorado no `trade_count` e no `hit_rate`, mas o PnL não realizado **já está** em `final_equity` via mark-to-market — logo entra em `total_pnl`. Consequência: `total_pnl` pode ser ≠ `soma dos pnl dos trades fechados`. Documentado e testado.

**Representação:** o `BacktestResult` ganha um novo campo opcional `metrics: BacktestMetrics | None` (default `None`), preenchido pelo engine antes de retornar. Ficar opcional mantém o schema retrocompatível com testes existentes no mesmo commit em que a API evolui.

## Consequences

- **Positive:** primeira caracterização mínima e honesta de um backtest; `None` explícito evita o vício clássico de confundir "estratégia sem trades" com "estratégia 0% hit rate"; funções puras continuam auditáveis e testáveis sem precisar de engine rodando.
- **Negative:** quatro métricas é pouco para decidir algo sério — e isso é proposital; esperar comparar estratégias com este conjunto é convidar conclusão errada. Até `ranking/scoring/` chegar, toda comparação é exploratória.
- **Neutral:** escolha de `max_drawdown` como fração positiva (não sinalizada) segue convenção mais comum e evita ambiguidade de sinal; documentado no schema.

## Alternatives considered

- **Incluir Sharpe/Sortino/profit factor já no mínimo** — rejeitado: Sharpe exige definição de período e taxa livre de risco; profit factor explode com zero-loss; são métricas razoáveis mas não mínimas. Ficam para a ADR futura de scoring multiobjetivo.
- **`hit_rate = 0.0` em ausência de trades** — rejeitado: confunde "não tentou" com "tentou e errou tudo". `None` carrega a informação correta.
- **Deixar `trade_count` incluir trades abertos ao fim** — rejeitado: hit rate sobre posição ainda aberta depende do preço de referência (mark-to-market); fica ambíguo. Regra "só trades fechados" é simples e auditável.
- **Viver em `ranking/scoring/` já** — rejeitado: `ranking/` é comparação entre estratégias, não caracterização de uma. Mover agora seria empurrar complexidade prematura.
- **Retornar drawdown em valor absoluto de equity em vez de fração** — rejeitado: fração é insensível à escala do capital, o que é o comportamento desejado para comparação com custos também expressos em bps.

## Follow-ups

- Implementar `src/alpha_forge/backtest/metrics.py` com `BacktestMetrics` (pydantic v2, frozen) e `compute_metrics` pura.
- Estender `BacktestResult` em `backtest/schemas.py` com `metrics: BacktestMetrics | None = None`; preencher no final de `run_backtest`.
- Emparelhar fills de entrada e saída durante o loop (o engine já tem a informação; basta registrar PnL realizado por trade em uma lista interna ao criar cada fill de saída).
- Atualizar `_print_summary` no CLI para imprimir as quatro métricas abaixo do output atual; `hit_rate` mostra `"n/a"` quando `None`.
- Escrever `tests/unit/test_backtest_metrics.py` cobrindo: zero trades → `hit_rate=None`, `max_drawdown=0.0`; equity flat → todos zero; trade aberto ao fim → `total_pnl` ≠ soma de trades fechados; sequência com 2 trades conhecidos → métricas conferem aritmeticamente.
- Atualizar `system/domain.md` (adicionar `BacktestMetrics`), `system/api.md` (nova função pública `compute_metrics` e campo novo em `BacktestResult`) e `system/flows.md` (sumário de `run-demo` agora inclui métricas) no mesmo commit da implementação.
