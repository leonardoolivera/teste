# 0131 — Série CZ9 closeout: MACX 10/30 não salva família, encerramento confirmado

**Status:** Accepted — família MACX completamente arquivada
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0130 (pré-reg), ADR-0125/0127/0129 (família CZ6/7/8)

## Resultado

| Tag | Asset/Janela | Tr | Sh | vs CZ6 (20/50) |
|---|---|---:|---:|---|
| CZ9.1 | BTC 2024-H2 bull | 63 | 1.88 | 2.39 → -0.5 |
| CZ9.2 | ETH 2024-H2 bull | 61 | **2.01** | 1.88 → +0.1 |
| CZ9.3 | SOL 2024-H2 bull | 64 | **0.16** | 1.22 → -1.1 (colapso) |
| CZ9.4 | BTC 2025-H2 misto | 63 | **-3.54** | -2.17 → pior |
| CZ9.5 | ETH 2025-H2 misto | 66 | **-2.61** | -1.47 → pior |
| CZ9.6 | SOL 2025-H2 misto | 69 | -1.02 | -2.44 → +1.4 |

## Interpretação

Lag menor (10/30 vs 20/50) **dobrou o número de trades** (~32 → ~63 por janela) mas:
- **Bull**: ganho marginal em ETH, perda em BTC, colapso em SOL → não há padrão de melhoria
- **Misto**: piora consistente em BTC e ETH; SOL só "melhora" porque o naked 20/50 era catastrófico

Conclusão: lag menor amplifica ruído em chop sem ganhar consistência em bull. Engine MACX é estruturalmente trend-follower que precisa de tendência sustentada — qualquer tentativa de "ser mais responsivo" piora o lado ruim sem ajudar o bom.

Gates pré-registrados:
- Engine viável naked (3/6 strict + 3/6 Sh ≥ -0.5): **2/6 strict + 0/6 Sh ≥ -0.5 em misto** → REFUTADO
- Salvamento parcial (4/6 Sh ≥ 0.5): 2/6 → REFUTADO
- Refutação família (<2/6 Sh ≥ 0.5): exatamente 2/6, na fronteira mas não evita refutação dado que misto é catastrófico

## Decisão

**Família MACX long ARQUIVADA definitivamente.** Variantes testadas:
- 20/50 naked (CZ6): 3/6 strict bull, 3/6 FAIL misto
- 20/50 + trend_htf (CZ7): 1/6 contextual
- 20/50 + bollinger_width (CZ8): 0/6 PASS
- 10/30 naked (CZ9): 2/6 strict, 3/6 FAIL profundo

## Padrão 36 (NOVO): variação de params não salva engine de problema estrutural

Quando engine falha por mecanismo estrutural (timing, lag, regime-dependence), variar parâmetros canônicos do mesmo mecanismo (10/30 vs 20/50, ambos cruzamento) não muda veredito — só desloca onde o problema aparece.

Implicação: Padrão 35 (exaustão de filter) + Padrão 36 (variação params não estrutural) → quando ambos se aplicam, engine arquivada sem testar mais variantes na mesma família.

Aplicação: MACX (long, qualquer params canônica) ARQUIVADO. MACX short não testado (short trend-follower é semanticamente confuso — vendo cruzamento bearish em downtrend?), mas baixa prior de valor no stack atual.

## Próximo possível (não agendado)

1. **Engine não-canônica**: implementar Keltner Channel, ATR breakout, vol-spike entry. Trabalho de código novo (não só sweep). Se família trend-following é o gap, precisa de mecanismo diferente — não mais médias móveis.
2. **Otimização mean-reversion existing**: bollinger_width thresholds (testar 200, 350, 400 bps em combos atuais), RSI bounds (25/75 vs 30/70).
3. **Reaceitar 13 combos como suficiente**: stack já tem 5 strict + 5 contextual + 3 grandfather. Diversificação por engine pode não ser alcançável com engines canônicas em 1h crypto.

## Ação executada

- ✅ ADR-0131 closeout
- ✅ Série CZ9 documentada
- ✅ STATE.md entry (consolidado tarde-3)

## Não-alvo

- Não testar MACX 50/200, 5/20, ou outras combinações (Padrão 36)
- Não testar MACX short
- Não promover nada
- Não alterar stack

## Stack pós-CZ9

13 combos inalterados.
