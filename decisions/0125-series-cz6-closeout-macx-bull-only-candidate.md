# 0125 — Série CZ6 closeout: MA Crossover 20/50 long é trend-follower regime-específico

**Status:** Accepted — gate atingido condicionalmente, candidato staging bull-only
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0124 (pré-registro), ADR-0117 (CY Donchian), Padrão 29

## Resultado

| Tag | Asset | Janela | Regime | Tr | Sh | Verdict |
|---|---|---|---|---:|---:|---|
| CZ6.1 | BTC | 2024-H2 | bull | 36 | **2.39** | strict |
| CZ6.2 | ETH | 2024-H2 | bull | 34 | **1.88** | strict |
| CZ6.3 | SOL | 2024-H2 | bull | 32 | **1.22** | strict |
| CZ6.4 | BTC | 2025-H2 | misto | 29 | -2.17 | FAIL |
| CZ6.5 | ETH | 2025-H2 | misto | 34 | -1.47 | FAIL |
| CZ6.6 | SOL | 2025-H2 | misto | 36 | -2.44 | FAIL |

**3/6 PASS strict em regime bull, 3/6 FAIL em regime misto.** Split perfeito por regime.

## Gate pré-registrado

- ≥3/6 Sh≥1.0 → abrir v-macrossover manifest → **atingido (3/6)**
- Ressalva: os 3 PASS são TODOS bull, os 3 FAIL são TODOS misto → padrão regime-dependente trivial

## Interpretação

MACX 20/50 long é **trend-follower puro** — exatamente como Donchian CY, mas mais suave:
- CY (Donchian 20/10) em bull: 0.71 / 0.11 / -0.91 (1/3 hit fraco)
- CZ6 (MACX 20/50) em bull: 2.39 / 1.88 / 1.22 (**3/3 strict — muito superior**)
- Ambos em misto: negativos consistentes

**Por que MACX supera Donchian em bull?** Donchian entra em breakout de máxima N-bar (suscetível a fake-out no topo); MACX entra em cruzamento de médias (lag maior, mas filtra whipsaw na entrada). Em bull sustentado, o lag compensa — entra um pouco tarde mas sai muito depois. Em chop, ambos perdem igualmente por falta de tendência.

## Decisão

**Candidato staging bull-only, não promoção direta a stack ativo.** Racional:

1. Gate técnico atingido (3/6 strict) mas condicional a regime bull. Promover sem filter = Padrão 29 outra vez (anti-diversificador destruidor em chop).
2. Stack atual (13 combos) opera em 2024-H2/2025-H1/2025-H2 — se MACX entrar sem filter, vai perder em 2/3 janelas.
3. Caminho certo: **regime-gated MACX** (ex: MACX + trend_htf long_only OU + bollinger_width max_bps alto = só trading em tendência). Isso é trabalho pra próxima série (CZ7 se rodar).

## Padrão 33 (NOVO): trend-follower requer regime filter obrigatório antes de promoção

Família trend-following (Donchian breakout, MA Crossover) tem edge forte em regime bull sustentado e destrutivo em chop/misto. Stack dominado por mean-reversion (RSI, Bollinger) tem perfil inverso.

Regra: **trend-follower só entra no stack com regime filter ativado** (trend_htf long_only OU bollinger_width min_bps). Promoção naked = Padrão 29 violation automática.

Corolário: CZ6 resultado (3/3 strict em bull) é evidence válida pra desenvolver v-macrossover-filtered em série futura, **NÃO pra abrir manifest naked**.

## Follow-up aberto (não agendado)

1. **CZ7 (futuro)**: MACX 20/50 long + trend_htf(4h,50,long_only) em todas 6 janelas CZ6 → se 4+/6 PASS strict → manifest real
2. **CZ8 (futuro)**: MACX com params diferentes (50/200, 10/30) — testar sensibilidade em 2024-H2 bull antes de gastar runs em cross-regime

## Ação executada

- ✅ ADR-0125 closeout
- ✅ Série CZ6 documentada
- ✅ STATE.md entry (consolidado CZ4+CZ5+CZ6)

## Não-alvo

- Não abrir manifest v-macrossover naked (Padrão 33)
- Não alterar stack

## Stack pós-CZ6

13 combos inalterados. Registry: MACX 20/50 long é candidato staging em bull puro (3/3 strict), PENDE regime filter.
