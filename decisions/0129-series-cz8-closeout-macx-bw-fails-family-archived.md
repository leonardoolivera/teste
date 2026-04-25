# 0129 — Série CZ8 closeout: bollinger_width(300) também falha; família MACX 20/50 arquivada

**Status:** Accepted — engine MACX 20/50 inviável para stack, família trend-following encerrada
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0128 (pré-reg), ADR-0127 (CZ7), ADR-0125 (CZ6), Padrões 33/34

## Resultado

**6/6 FAIL.** Wipeout total — pior que CZ7.

| Tag | Asset/Janela | Tr nk→ft | Sh nk→ft |
|---|---|---|---|
| CZ8.1 | BTC 2024-H2 bull | 36→12 | 2.39→**-1.60** |
| CZ8.2 | ETH 2024-H2 bull | 34→12 | 1.88→**-1.43** |
| CZ8.3 | SOL 2024-H2 bull | 32→21 | 1.22→-0.08 |
| CZ8.4 | BTC 2025-H2 misto | 29→9 | -2.17→-1.03 |
| CZ8.5 | ETH 2025-H2 misto | 34→16 | -1.47→**-2.89** |
| CZ8.6 | SOL 2025-H2 misto | 36→26 | -2.44→-1.65 |

## Interpretação

bollinger_width(300bps) ativa quando vol já está alta. MACX 20/50 é entry com lag de cruzamento. Combinação:
1. Filter espera vol expansão
2. Quando filter libera, breakout já aconteceu
3. Cruzamento MACX dispara mais tarde ainda
4. Entrada chega na fase de mean-reversion pós-extensão → loss

O filter que parecia salvador (sem lag composto, Padrão 34) na verdade **piora MACX por outro mecanismo**: timing de ativação assíncrono com cruzamento.

CZ6 (naked) + CZ7 (trend_htf) + CZ8 (bollinger_width) cobrem as 3 categorias canônicas de filter (nenhum, lag-direcional, vol-regime). **Todos falham ou degradam.**

## Decisão final MACX 20/50 long

**ARQUIVADO definitivamente.** Conclusão estrutural (não window-specific):

| Variante | Resultado |
|---|---|
| Naked (CZ6) | 3/6 strict bull, 3/6 FAIL misto — Padrão 33 veta |
| + trend_htf(4h,50) (CZ7) | 1/6 contextual, lag composto destrói edge |
| + bollinger_width(300) (CZ8) | 0/6 PASS, timing assíncrono destrói edge |

Engine MACX 20/50 long é **bull-only sem mecanismo viável de gating**. Saída do candidato staging: definitiva.

## Padrão 35 (NOVO): exaustão de combo engine+filter define inviabilidade estrutural

Quando uma engine falha em (a) naked + (b) filter direcional HTF + (c) filter vol-regime, é razoável **arquivar a engine inteira na configuração testada** sem precisar rodar mais combinações exóticas. As 3 categorias cobrem o espaço de gating canônico — extensões adicionais (filter custom, multi-filter) têm baixa prior probability de inverter o veredito.

Aplicação: MACX 20/50 long fica arquivado. Variantes (10/30, 50/200) continuam abertas como exploração de **parâmetros**, não como tentativa de salvar 20/50.

## Família trend-following 1h: status final

Resumo das 3 séries que cobriram família trend-following 1h em 2026-04-20:

| Engine | Série | Resultado |
|---|---|---|
| Donchian 20/10 long | CY (ADR-0117) | 1/6 hit fraco, anti-diversificador (Padrão 29) |
| MACX 20/50 long naked | CZ6 (ADR-0125) | 3/6 strict bull, 3/6 FAIL misto (Padrão 33) |
| MACX 20/50 + trend_htf | CZ7 (ADR-0127) | 1/6 contextual, lag composto (Padrão 34) |
| MACX 20/50 + bw(300) | CZ8 (este) | 0/6 PASS, timing assíncrono (Padrão 35) |

**Família encerrada.** Stack permanece dominado por mean-reversion (RSI, Bollinger). Diversificação por engine continua sendo o gap aberto, mas as ideias canônicas trend-following 1h estão exauridas.

## Próximo possível (não agendado)

1. **MACX 50/200**: timeframe maior ainda, lag pior — improvável, mas teste de sensibilidade
2. **MACX 10/30**: lag menor, mais trades, possivelmente vira algo
3. **Engine não-canônica**: vol-breakout (entry on vol spike sem MA), Keltner channel, ATR-based — exigiria implementar nova engine
4. **Gap de diversificação aceito**: continuar otimizando mean-reversion existing

## Ação executada

- ✅ ADR-0129 closeout
- ✅ Série CZ8 documentada
- ✅ STATE.md entry (consolidado CZ7+CZ8)

## Não-alvo

- Não testar mais variantes MACX 20/50 (Padrão 35)
- Não promover nada
- Não alterar stack

## Stack pós-CZ8

13 combos inalterados.
