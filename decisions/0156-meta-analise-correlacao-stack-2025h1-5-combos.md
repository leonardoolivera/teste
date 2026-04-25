# 0156 — Meta-análise: correlação stack 2025-H1 (5 combos short) + Padrão 43

**Status:** Accepted — análise descritiva, nenhuma edição de manifest. Padrão 43 formalizado.
**Date:** 2026-04-20
**Deciders:** Usuário ("só vai, proxima") + agente
**Relates to:** Padrão 29 (anti-diversificador), Padrões 22-42 (exploração família completa)

## Motivação

13 combos ativos nunca foram analisados cross-combo. Após Bollinger family totalmente sensibilizada (CZ14-19) sem upgrades disponíveis via 1-knob, meta-análise pode revelar: (a) se stack é realmente diversificado, (b) quais combos são redundantes, (c) onde abrir próxima frente de pesquisa.

Escopo: 5 combos 2025-H1 (janela com maior overlap temporal). Matriz de correlação Pearson de retornos hora-a-hora das equity curves walk-forward.

## Resultado

3475 timestamps alinhados, correlação pareada:

| Par | Correlação |
|---|---:|
| bol_short_BTC ↔ rsi_short_width_BTC | **+0.610** |
| bol_short_ETH ↔ bol_short_SOL | +0.463 |
| bol_short_BTC ↔ bol_short_SOL | +0.387 |
| bol_short_SOL ↔ rsi_short_width_BTC | +0.362 |
| bol_short_ETH ↔ rsi_short_trendhtf_SOL_2575 | +0.343 |
| bol_short_BTC ↔ bol_short_ETH | +0.340 |
| bol_short_ETH ↔ rsi_short_width_BTC | +0.289 |
| bol_short_SOL ↔ rsi_short_trendhtf_SOL_2575 | +0.258 |
| bol_short_BTC ↔ rsi_short_trendhtf_SOL_2575 | +0.220 |
| rsi_short_width_BTC ↔ rsi_short_trendhtf_SOL_2575 | **+0.173** |

**Estatísticas**: média off-diagonal = +0.345; máx = +0.610; mín = +0.173.

## Interpretação

### 1. Stack parcialmente diversificado

Média de correlação +0.345 indica stack **parcialmente diversificado** — melhor que 1 combo único (que teria corr=1 com si mesmo), mas longe de ortogonal. Nenhum par > 0.7 (threshold de redundância perigosa).

Comparação referência: 2 combos idênticos teriam corr=1.0; 2 combos totalmente ortogonais teriam corr=0.0. +0.345 = cerca de 35% do retorno é "tendência comum do mercado crypto 2025-H1 short" e 65% é edge específico de cada combo.

### 2. BTC-BTC mesmo-filter é o par mais redundante

Maior correlação (+0.610) ocorre entre 2 combos BTC short + width filter mas engines diferentes (Bollinger vs RSI). Engines distintos **não desdiversificam como esperado** quando asset+direção+filter são iguais. Isso é empiricamente novo — contradiz a suposição implícita de que "famílias diferentes = diversificação automática".

Implicação: se stack tem 2 combos em mesmo asset/filter/direção, pagar custo de manter ambos é marginal. **rsi_short_width_BTC** e **bol_short_BTC** entregam ~60% do mesmo retorno.

### 3. Asset é fator de maior peso em diversificação

Pares cross-asset com mesma direção + família:
- BTC ↔ ETH ↔ SOL (todos bol_short + width): +0.34 a +0.46 (correlação moderada)

Pares cross-asset com filter diferente:
- rsi_short_width_BTC ↔ rsi_short_trendhtf_SOL_2575: **+0.173** (baixa, melhor diversificação)

Ordem empírica de poder diversificador: **asset > filter type > engine family**.

### 4. trend_htf filter é o mais diversificador

`rsi_short_trendhtf_SOL_2575` aparece nos 4 pares de menor correlação com todos outros combos (+0.17 a +0.34). Filter trend_htf seleciona regimes de retorno diferente do width filter — combos com trend_htf são **anti-diversificador** natural do resto do stack.

Implicação: manter sempre ≥1 combo trend_htf no stack preserva diversificação estrutural.

## Padrão 43 (NOVO): engine family não desdiversifica sozinha

**"Combos em mesmo asset + direção + filter têm correlação elevada (~0.6) mesmo quando engines são de famílias diferentes (Bollinger vs RSI). Engine family sozinha é fraca fonte de diversificação; asset e filter type são mais poderosos. Stack com 2 combos redundantes em (asset, direção, filter) extrai apenas ~40% de retorno adicional vs 1 combo.**

**Implicações prospectivas:**
1. Não multiplicar combos variando apenas engine family quando tudo resto é igual — baixo retorno de diversificação.
2. Priorizar diversificação via asset novo ou filter diferente.
3. trend_htf filter produz descorrelação estrutural maior que width filter — preservá-lo no stack.
4. Em promoções futuras, incluir check de correlação com stack existente: se novo candidato tiver corr > 0.7 com combo existente, escopo é redundância não edge novo."**

## Decisão

- Nenhuma edição de manifest baseada apenas nesta análise descritiva
- Registrar Padrão 43 para uso prospectivo
- Manter ambos combos BTC-width (bol + rsi) — corr 0.61 é alta mas < 0.7; retorno marginal ainda existe
- Não remover rsi_short_trendhtf_SOL_2575 — é âncora de descorrelação do stack

## Próximas frentes candidatas (pós-meta-análise)

Com Padrão 43 formalizado, pesquisa futura deve priorizar:

1. **Filter diferente em asset existente**: testar bollinger_short + trend_htf (atualmente só width) — potencialmente mais diversificador que variar engine
2. **Asset novo**: ingest DOT/AVAX/LINK destravaria nova dimensão (asset é fator dominante)
3. **Composição AND de filters**: width AND trend_htf — Padrão 17 exige pernas FAIL isoladas; testar se combinação seleciona regime super-específico
4. **Expansão temporal**: 2025-H2 combos já existem mas nunca correlacionados — meta-análise 2025-H2 análoga

## Ação executada

- ✅ Script `tools/analyze_stack_correlation_2025h1.py` criado
- ✅ Matriz salva em `exports/diag/stack_correlation_2025h1.json`
- ✅ ADR-0156 com Padrão 43
- ⏳ STATE.md tarde-13 entry

## Não-alvo

- Não tocar manifests — análise descritiva pura
- Não extrapolar para assets/janelas não-2025-H1 (matriz única)
- Não usar correlação walk-forward como substituta de paper-trade real (estimativa ex-ante)

## Limitações metodológicas

- Correlação Pearson é linear; pode subestimar dependência em cauda (crashes conjuntos)
- 3475 timestamps de 2025-H1 apenas; resultado pode diferir em 2024-H2 bull ou 2025-H2 misto
- Equity curves vêm de walk-forward (não backtests full-period), pequenas descontinuidades entre folds
- Não inclui combos 2024-H1/H2 (seria necessário alinhar janelas diferentes separadamente)
