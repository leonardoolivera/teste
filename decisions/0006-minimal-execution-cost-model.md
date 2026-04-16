# 0006 — Minimal execution cost model

**Status:** Accepted
**Date:** 2026-04-16
**Deciders:** Usuário (owner do projeto) + agente.

## Context

O núcleo mínimo atual executa a `t+1 open` sem atrito. Resultados "limpos demais" escondem fragilidade: a diferença entre uma estratégia com edge real e uma ilusão estatística costuma viver justamente nos custos. `vision/01-product.md` elevou "custo real antes de retorno bruto" a princípio de produto.

Antes de introduzir métricas (ADR-0007) ou a primeira estratégia séria, precisamos que o motor cobre atrito de forma explícita, determinística e auditável. Não é o modelo completo de custos — é o mínimo honesto que impede a métrica de nascer viciada.

## Decision

O modelo mínimo de custos do Alpha Forge aplica **dois componentes, combinados no preço de execução**, nunca como ajuste separado sobre PnL:

1. **Taker fee base (bps).** Campo `taker_fee_bps: float ≥ 0` em um novo `CostModel` (pydantic v2, frozen). Um valor de `5.0` significa 5 basis points = 0,05%. Aplicado em toda entrada e toda saída.
2. **Slippage linear por notional (bps).** Campo `slippage_bps_per_unit_notional: float ≥ 0` no mesmo `CostModel`. Slippage efetivo em bps = `slippage_bps_per_unit_notional * (notional / capital_inicial)`. Penaliza trades grandes relativos ao capital; trade infinitesimal → slippage ≈ 0.

**Aplicação determinística no preço de execução:**

- Entrada long: `price_effective = price_market * (1 + total_bps / 10_000)`.
- Entrada short: `price_effective = price_market * (1 - total_bps / 10_000)`.
- Saída long: `price_effective = price_market * (1 - total_bps / 10_000)`.
- Saída short: `price_effective = price_market * (1 + total_bps / 10_000)`.

Onde `total_bps = taker_fee_bps + slippage_bps_per_unit_notional * (notional / capital_inicial)`. Direção do ajuste sempre contra o trader — é atrito, não prêmio.

**Exposto via `run_backtest(..., cost_model: CostModel)` como argumento obrigatório.** Sem default silencioso: todo backtest declara seu modelo de custos. Valor-zero é permitido mas tem que ser explícito (`CostModel(taker_fee_bps=0.0, slippage_bps_per_unit_notional=0.0)`), deixando claro "rodei sem custos".

**Explicitamente fora do escopo desta fase** (cada item vira ADR futura quando a necessidade aparecer):

- Maker fee / logic de ordens limit.
- Funding cost em perpétuos.
- Spread sintético (bid-ask).
- Modelo de custo dependente de ativo, exchange ou horário.
- Impacto não-linear de market size (`sqrt`, `power-law`).
- Latência / fila de ordens.
- Fees por volume/tier.

## Consequences

- **Positive:** métrica nasce sobre resultado com atrito; trades grandes pagam mais, forçando estratégias a serem sensatas em sizing; aplicação no preço (não no PnL separado) mantém rejeição de sizing e contrato causal intocados.
- **Negative:** a linearidade do slippage é uma aproximação grosseira — estratégias que naturalmente abrem grandes posições serão castigadas de forma possivelmente otimista; não cobre funding, que é central em perp crypto (aceitável para o núcleo mínimo, inaceitável quando chegarmos ao primeiro dataset real).
- **Neutral:** `CostModel` como argumento obrigatório quebra a assinatura anterior de `run_backtest` — ajuste único, com teste de integração atualizado no mesmo commit.

## Alternatives considered

- **Fee como ajuste de PnL ao fechar trade** — rejeitado: separa contabilidade de execução, complica rejeição determinística (um fill "aprovado" viraria PnL "inválido" depois), e esconde o custo do guardião causal que opera sobre preços.
- **Slippage constante em bps, sem função do notional** — rejeitado: incentivaria indiretamente sizing exagerado, exatamente o oposto do desejado em um laboratório de estratégias agressivas com leverage.
- **Já incluir funding no mínimo** — rejeitado nesta fase: funding em perp depende de série adicional (funding rate por barra), amplia o manifesto, e merece ADR dedicada junto com o primeiro dataset real.
- **Default silencioso zero** — rejeitado: "rodei sem custos" precisa aparecer na configuração, não ser o comportamento padrão.

## Follow-ups

- Implementar `src/alpha_forge/backtest/cost.py` com `CostModel` (pydantic v2, frozen) e função pura `apply_cost(price, notional, capital_inicial, side_direction, cost_model) -> float`.
- Alterar `run_backtest` em `backtest/engine.py` para receber `cost_model: CostModel` obrigatório; aplicar no preço antes de criar o `Fill`; preservar os campos atuais do `Fill` (preço passa a ser o efetivo pós-custo).
- Atualizar CLI `run-demo` com flags `--taker-fee-bps` e `--slippage-bps-per-notional`, sem default implícito zero na API (a CLI pode passar zero, mas explicitamente).
- Atualizar `tests/integration/test_minimal_flow.py` e acrescentar `tests/unit/test_cost_model.py` verificando: zero-custo não altera preços; taker fee aplicado nas 4 direções (entrada/saída × long/short); slippage escala linear com notional/capital; trade com `notional == capital_inicial` paga exatamente `taker_fee_bps + slippage_bps_per_unit_notional`.
- Atualizar `system/domain.md` (adicionar `CostModel`), `system/api.md` (nova assinatura de `run_backtest`) e `system/flows.md` (passo extra no `run-demo`) no mesmo commit da implementação.
