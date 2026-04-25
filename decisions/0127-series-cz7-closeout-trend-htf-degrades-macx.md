# 0127 — Série CZ7 closeout: trend_htf(4h,50) degrada MACX 1h, MACX inviável p/ stack

**Status:** Accepted — filter rejeitado, MACX 20/50 fechado para stack
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0126 (pré-reg), ADR-0125 (CZ6), Padrão 33

## Resultado

| Tag | Asset/Janela | Tr nk→ft | Sh nk→ft | Δ |
|---|---|---|---|---|
| CZ7.1 | BTC 2024-H2 bull | 36→14 | 2.39→**1.61** | preserva (degradação leve) |
| CZ7.2 | ETH 2024-H2 bull | 34→14 | 1.88→**-0.06** | colapso |
| CZ7.3 | SOL 2024-H2 bull | 32→13 | 1.22→0.24 | colapso |
| CZ7.4 | BTC 2025-H2 misto | 29→8 | -2.17→-2.89 | piora |
| CZ7.5 | ETH 2025-H2 misto | 34→7 | -1.47→-0.26 | salva nominal, Sh inalterado |
| CZ7.6 | SOL 2025-H2 misto | 36→9 | -2.44→-1.60 | salva nominal |

**1/6 PASS contextual, 0/6 strict, 4/6 FAIL.**

## Interpretação

Filter trend_htf(4h, sma=50, long_only) corta ~60% dos trades em todas janelas. Hipótese inicial era que o filter eliminaria trades em chop (2025-H2) preservando bull (2024-H2). Resultado real: **filter destrói o edge bull em 2/3 ativos** — ETH e SOL colapsam, só BTC mantém contextual.

**Razão estrutural** (Padrão 31 reforçado): MACX já tem lag intrínseco de cruzamento. trend_htf(4h, sma=50) adiciona segundo lag (200h ≈ 8 dias HTF). Lag composto = entrada muito tarde no bull, perde a fase explosiva. Em 1h base, cruzamento MACX dispara já no início da tendência; com filter HTF exigindo confirmação macro, MACX só entra quando já está esticado.

**Por que BTC sobreviveu?** Tendência BTC 2024-H2 foi mais sustentada que ETH/SOL (menor vol, breakouts mais longos). Filter ainda cortou Sharpe (2.39 → 1.61) mas não destruiu.

## Decisão

**MACX 20/50 long FECHADO para stack.** Gates pré-registrados (ADR-0126):
- Promoção (4+/6 strict): 0/6 → REFUTADO
- Salvamento staging (≤1/6 Sh<0): 4/6 FAIL → REFUTADO
- Refutação confirmada (filter degrada bull <2/6 Sh≥1.0): 1/6 → confirmada

Não rodar MACX naked tampouco — Padrão 33 vetou e CZ7 mostrou que o filter canônico não funciona. MACX 20/50 sai do candidato staging.

## Padrão 34 (NOVO): lag composto invalida MACX + filter HTF

Estratégias com lag intrínseco (cruzamento de médias) NÃO se beneficiam de filter HTF baseado em SMA longa. Lag total = lag_engine + lag_filter; em entradas trend-following, isso traduz em entrada tardia e missing da fase rentável.

Implicação:
- Trend-followers com **lag baixo** (Donchian breakout) podem usar trend_htf, mas refutados por outras razões (Padrão 29 anti-diversificador).
- Trend-followers com **lag alto** (MACX, MA Triple) precisam de filter SEM lag adicional: vol-regime (bollinger_width), volume spike, ou price-action puro (não SMA HTF).
- Mean-reversion (RSI, Bollinger short) tem lag mínimo + filter HTF complementa bem (CZF/CT.1 mostraram).

## Próximo possível (não agendado)

1. **CZ8**: MACX 20/50 + bollinger_width (regime filter, sem lag adicional) — testar Padrão 34 corolário positivo
2. **CZ9**: MACX 50/200 ou 10/30 — sensibilidade params, mas só se filter for resolvido
3. **Família trend-following arquivada**: MACX naked (CZ6) + filtered (CZ7) ambos inviáveis. Donchian (CY) anti-diversificador. **Sem trend-follower no stack até nova ideia.**

## Ação executada

- ✅ ADR-0127 closeout
- ✅ Série CZ7 documentada
- ✅ STATE.md entry (consolidado CZ7+CZ8)

## Não-alvo

- Não promover MACX a stack
- Não testar mais variantes MACX antes de tentar bollinger_width filter (Padrão 34 corolário)
- Não alterar stack

## Stack pós-CZ7

13 combos inalterados. Registry: MACX 20/50 long REJEITADO definitivamente (naked CZ6 = regime-dependent + filtered CZ7 = degrada bull).
