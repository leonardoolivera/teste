# 0012 — Donchian cost monotonicity property test

**Status:** Accepted
**Date:** 2026-04-17
**Deciders:** givesefie (autor), risk-auditor (revisor)

## Context

A [ADR-0010](./0010-cost-monotonicity-property-test.md) estabeleceu a invariante de monotonicidade de custo em `final_equity` como infraestrutura de confiança do cost model — mas o property test atual cobre **apenas** `MovingAverageCrossoverStrategy(20, 50)` sobre o sintético seminal. O piloto Donchian (ADR-0011) continua sem property coverage para esta invariante. O blocker #B-2 do [AUDIT.md](../AUDIT.md) é explícito: "Property-based de monotonicidade de custo para Donchian não foi escrito. ADR-0010 cobre só MA crossover. Donchian continua coberto apenas pela checagem grosseira do `validate_pilot.py`."

## Decision

Estender ADR-0010 com um segundo property test, **estruturalmente idêntico** (mesmos componentes, mesma tolerância, mesma fixture), trocando apenas a estratégia: `DonchianBreakoutStrategy(entry_window=20, exit_window=10)`. Mesmo dataset sintético, mesmo budget, mesma invariante em `final_equity`. Nenhum parâmetro novo; apenas replicação do padrão.

## Consequences

- **Positive:** blocker #B-2 do AUDIT fechado. ADR-0010 vira política efetiva (aplicada a toda estratégia do lab), não exceção aplicada só a MA crossover. Regressões no cost model afetando Donchian passam a falhar CI.
- **Negative:** tempo de suíte aumenta (~15–20s a mais — 30 exemplos × 2 backtests de 720 barras). Aceitável.
- **Neutral:** padrão estabelecido: cada nova estratégia aceita pelo lab ganha um property de monotonicidade de custo próprio no mesmo estilo. Não é diretiva dura; é precedente.

## Alternatives considered

- **Parametrizar o test existente por estratégia** — rejeitado porque mistura responsabilidades: `test_cost_monotonicity.py` documenta a invariante; um test por estratégia documenta a aplicação a cada família. Padrão mais legível.
- **Generalizar para "toda Strategy"** via `hypothesis.strategies.sampled_from` de classes — rejeitado: adiciona complexidade e acopla o test à enumeração de estratégias; preferimos um arquivo por família, explícito.
- **Adiar até ter grid search completo** — rejeitado: o property é ortogonal ao grid search. Fecha B-2 sozinho; não depende de B-3/B-4/B-5.

## Follow-ups

Cada um vira linha em `STATE.md`:

- Criar `tests/property/test_donchian_cost_monotonicity.py` no mesmo molde de `tests/property/test_cost_monotonicity.py`.
- Atualizar `AUDIT.md` marcando B-2 como resolvido; atualizar `CHECKLIST.md` marcando o gate de monotonicity como verde.
- Atualizar `STATE.md` com a entrega.
