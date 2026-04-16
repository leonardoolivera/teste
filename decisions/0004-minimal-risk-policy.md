# 0004 — Política mínima de risco e sizing (núcleo mínimo)

**Status:** Accepted
**Date:** 2026-04-16
**Deciders:** Usuário (owner do projeto) + agente.

## Context

`vision/02-scope.md` estabeleceu `risk/` como módulo separado de `backtest/` (governança vs simulação). O núcleo mínimo precisa de uma política de sizing para que uma estratégia dummy produza uma curva de equity plausível, sem que sizing vire um subsistema prematuramente. Toda tentação de "sizing adaptativo por volatilidade desde já" foi recusada pelo usuário — o núcleo mínimo deve ser o **menor risco possível compatível com um backtest honesto**.

Esta ADR fixa o escopo mínimo. ADR posterior (a ser escrita quando a fase `building` amadurecer) expandirá para política completa de risco (composite budgets, aggregate exposure, ruin guard, equity guard, volatility sizing).

## Decision

Para o núcleo mínimo, `risk/` implementa **apenas duas coisas**:

1. **`RiskBudget` (pydantic v2):** estrutura que declara `capital_inicial: float`, `fracao_por_trade: float` (entre 0 e 1), `alavancagem_max: float` (entre 1 e 10). Sem mais campos. O limite de `10.0` em `alavancagem_max` é **hard cap, não sugestão** — valor fora da faixa é rejeitado pelo validador pydantic.
2. **`fixed_fractional_position_sizing(budget, preco_entrada) -> tamanho_posicao`:** função **pura e determinística** (sem estado, sem I/O, sem aleatoriedade) que retorna o tamanho da posição em unidades do ativo, dado o `RiskBudget` e o preço de entrada. Aplica a alavancagem declarada no budget, sem ajuste dinâmico.

**Regra de rejeição determinística no engine.** O engine de backtest é obrigado a rejeitar a ordem, sem executar, quando o tamanho calculado por sizing for qualquer um dos seguintes:

- zero ou negativo;
- `NaN`;
- `+inf` ou `-inf`;
- tal que a exposição resultante (`tamanho * preco_entrada / capital_disponível`) ultrapasse `alavancagem_max` do budget vigente.

Rejeição é silenciosa para o resultado (nenhum trade acontece) mas **ruidosa para o log** (evento estruturado com motivo). Não há fallback automático — um sizing inválido indica bug e deve ser visto, não contornado.

**Explicitamente fora do escopo desta fase** (cada item vira follow-up de ADR separada quando a fase `building` justificar):

- Sizing por volatilidade (ATR, stddev, parkinson, etc.).
- Composite budgets (múltiplas contas, sub-alocações).
- Aggregate risk (risco de portfólio, correlações, exposição agregada).
- Equity guard / ruin guard (desligar estratégia abaixo de threshold).
- Stop-loss dinâmico ou take-profit adaptativo.
- Funding cost budget, margin call simulation.

Estratégia no núcleo mínimo usa **uma única** `RiskBudget` por execução. Sem perfis, sem composição.

## Consequences

- **Positive:** o módulo `risk/` nasce como governança mínima e clara; impossível confundir com engine de backtest; sizing é determinístico e auditável; alavancagem fica declarada e limitada.
- **Negative:** uma estratégia com alta volatilidade e outra com baixa volatilidade vão apostar o mesmo tamanho relativo; isso é ruim para ranking real — mas o núcleo mínimo não faz ranking comparativo, só prova o pipeline.
- **Neutral:** o limite superior de 10x alavancagem (alinhado com `vision/01-product.md`) é declarado mas não imposto por validador separado; a estrutura pydantic recusa valores fora do intervalo.

## Alternatives considered

- **Sizing por volatilidade desde já (ATR-based)** — rejeitado: é uma decisão que depende de caracterização de regime e de fricção real, ambas ausentes no núcleo mínimo; introduzir agora contamina a prova de pipeline com complexidade desnecessária.
- **Só `fraction_of_equity` fixo, sem `RiskBudget` estruturado** — rejeitado: deixar sizing como `float` solto em configs espalha regra de governança pelo código, exatamente o que `risk/` tem a missão de evitar.
- **Incluir equity guard mínimo ("se drawdown > X, pare")** — rejeitado para esta fase: é governança importante mas adiciona um segundo eixo de comportamento; fica como ADR futura antes da primeira estratégia não-dummy.

## Follow-ups

- Implementar `src/alpha_forge/risk/schemas.py` com `RiskBudget` (pydantic v2, validadores para faixas; `alavancagem_max` ∈ [1, 10] como hard cap).
- Implementar `src/alpha_forge/risk/sizing.py` com `fixed_fractional_position_sizing` como função pura e determinística.
- Integrar a regra de rejeição determinística no `backtest/engine.py`: antes de abrir posição, validar que o tamanho não é zero/negativo/NaN/inf e que a exposição resultante respeita `alavancagem_max`. Emitir evento de log estruturado em caso de rejeição.
- Escrever `tests/unit/test_risk_sizing.py` com casos: alavancagem 1x, alavancagem 10x, fração inválida (>1 ou <0) levanta erro, capital zero levanta erro, preço zero/negativo/NaN é tratado pela regra de rejeição do engine.
- Escrever `tests/unit/test_engine_reject_invalid_sizing.py` cobrindo os cinco gatilhos de rejeição (zero, negativo, NaN, inf, acima do hard cap).
- Abrir ADR-0007 (política de risco completa) quando a primeira estratégia não-dummy for implementada: escopo esperado inclui volatility sizing, equity guard, aggregate exposure.
