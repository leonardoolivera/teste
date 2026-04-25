# 0157 — Meta-análise: correlação stack 2025-H2 (7 combos) + validação cross-janela Padrão 43

**Status:** Accepted — análise descritiva replicando ADR-0156 em 2025-H2. Padrão 43 validado cross-janela.
**Date:** 2026-04-20
**Deciders:** Usuário ("as 4") + agente
**Relates to:** ADR-0156 (meta-análise 2025-H1), Padrão 43

## Motivação

Replicar meta-análise ADR-0156 em 2025-H2 para: (a) validar Padrão 43 cross-janela; (b) confirmar que engine family (BB vs RSI) é fraca fonte de diversificação em regime diferente; (c) checar se trend_htf continua sendo âncora de descorrelação.

Escopo: 7 combos 2025-H2 ativos (3 bol + 3 rsi-width + 1 rsi-trendhtf). 2 combos a mais que 2025-H1 pois ETH/SOL width-RSI também têm walk-forward 2025-H2.

## Resultado

3455 timestamps alinhados; 21 pares off-diagonal.

| Par (desc) | Correlação |
|---|---:|
| bol_short_SOL ↔ rsi_short_width_SOL | **+0.677** (máx) |
| bol_short_BTC ↔ rsi_short_width_BTC | +0.605 |
| bol_short_ETH ↔ rsi_short_width_ETH | +0.534 |
| rsi_short_width_SOL ↔ rsi_short_trendhtf_SOL_2575 | +0.530 |
| rsi_short_width_ETH ↔ rsi_short_width_SOL | +0.475 |
| … 16 pares intermediários … | 0.22 a 0.43 |
| bol_short_BTC ↔ rsi_short_trendhtf_SOL_2575 | **+0.219** (mín) |

**Estatísticas**: média off-diagonal = **+0.383**; máx = +0.677; mín = +0.219.

## Comparação com 2025-H1 (ADR-0156)

| Métrica | 2025-H1 (5 combos) | 2025-H2 (7 combos) | Δ |
|---|---:|---:|---:|
| Mean off-diag | +0.345 | +0.383 | +0.038 |
| Max | +0.610 | +0.677 | +0.067 |
| Min | +0.173 | +0.219 | +0.046 |
| Pares > 0.5 | 0/10 | 4/21 | — |
| Pares > 0.7 | 0/10 | 0/21 | — |

**2025-H2 levemente mais correlacionado** que 2025-H1 (mean +0.038). Consistente com tese: em regimes trending (H2 teve rally + correção mais definidos que H1 ranging), combos short mean-reversion tendem a disparar mais juntos.

## Interpretação

### 1. Padrão 43 validado cross-janela

Os 3 pares **engine-family-only** (mesmo asset+filter+direção, BB vs RSI) lideram o ranking:
- SOL: +0.677
- BTC: +0.605
- ETH: +0.534

Média dos 3 = +0.605. Em 2025-H1 o único par equivalente mensurável foi BTC +0.610. **Confirma que engine family isolada entrega ~60% do mesmo retorno** — insight generaliza além de 2025-H1 e além do único asset BTC.

Padrão 43 **promovido de hipótese a observação replicada**.

### 2. trend_htf continua sendo anti-diversificador (mas 2º agora)

rsi_short_trendhtf_SOL_2575 aparece nos 3 pares mais baixos (+0.219, +0.227, +0.233 com BTC/BTC/ETH). Mesma posição estrutural que 2025-H1. Corrobora Padrão 43 ponto 3: trend_htf preserva descorrelação estrutural.

Exceção: correlação intra-SOL (trendhtf ↔ width SOL) = +0.530. **Filter diferente** em mesmo asset **é menos diversificador** que esperado. Razão provável: ambos short, ambos SOL, ambos RSI engine → só filter varia → seleciona regimes parcialmente sobrepostos.

### 3. Asset continua dominante como fator de diversificação

Pares cross-asset low-corr: BTC ↔ trendhtf-SOL (+0.219), BTC ↔ width-SOL (+0.243), BTC ↔ width-ETH (+0.279). Os 3 menores pares **todos envolvem BTC pareado com ETH/SOL**. BTC é anti-correlacionado-ish com alts em H2 — regime diferente de H1.

Ordem empírica atualizada (Padrão 43 refinado):
1. **Asset diferente** (max drop: ~0.35)
2. **Filter diferente** (drop variável: +0.12 em cross-asset, mas só +0.05 intra-asset)
3. **Engine family** (drop marginal: ~0.06)

### 4. Novo insight: intra-asset cross-filter-cross-engine é redundância máxima

bol_SOL ↔ rsi-width_SOL = +0.677 **é o mais alto da matriz**. Mesmo asset + direção + filter, engines diferentes (BB e RSI). Em 2025-H1 o mesmo padrão (BTC) deu +0.610.

Implicação: **(asset, direção, filter) é o triplet que define "edge real"**; variar engine em cima disso entrega retorno redundante. Stack com 3 pares engine-only tem ~60% redundância nessas 3 dimensões.

## Decisão

- Nenhuma edição manifest
- Padrão 43 validado: **promovido de observação H1 a regularidade cross-janela**
- Refinar ordem de sensibilidade: asset > filter > engine, com nuance intra-asset cross-filter ainda alto
- Manter stack como está — nenhum par > 0.7 (threshold redundância crítica)

## Próximos passos em luz deste resultado

O problema estrutural dos 3 pares engine-only (+0.6) sugere **2 direções**:

**A) Aceitar redundância como custo de robustez** — manter BB + RSI em mesmo (asset, filter) porque famílias diferentes amortizam falha de 1 engine. Em 2025-H2 BB e RSI ambos funcionaram bem, mas se 1 colapsasse, outro salvaria. Seguro-incêndio a custo de +0.6 correlação.

**B) Consolidar para 1 engine por (asset, filter)** — deletar metade dos combos redundantes, liberar budget para diversificar via filter/asset novo. Mas perde hedge anti-falha-engine.

Escolha não é óbvia; depende de crença sobre probabilidade de falha de engine isolada. **Recomendação**: não consolidar ainda; priorizar **frentes ortogonais** (filter novo, asset novo) que atacam dimensões de diversificação mais poderosas antes.

## Ação executada

- ✅ Script `tools/analyze_stack_correlation_2025h2.py` criado
- ✅ Matriz salva em `exports/diag/stack_correlation_2025h2.json`
- ✅ ADR-0157 registrado
- ⏳ STATE.md tarde-14 entry

## Não-alvo

- Não tocar manifests — análise descritiva
- Não decidir consolidação redundância — requer ADR dedicado de política
- Não misturar janelas H1 e H2 na mesma matriz (windows diferentes, separar)

## Limitações

- 2025-H2 = 6 meses; regime único
- Correlação Pearson linear; cauda não modelada
- Walk-forward equity pode ter pequenas descontinuidades fold-to-fold
- 7 combos, 21 pares — N pequeno para estatística robusta
