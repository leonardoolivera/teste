# 0121 — Série CZ4 closeout: trend_htf(1d) refutado para SOL RSI short 4h

**Status:** Accepted — filter rejeitado, staging CZ2 permanece inalterado
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0120 (pré-registro), ADR-0119 (CZ2 staging), ADR-0084 (v6 trend_htf 1h rescue)

## Resultado agregado

Baseline naked vs filtered (trend_htf:htf=1d:sma=20:short_only):

| Tag | Janela | Regime | Tr nk→ft | Sh nk→ft | Verdict |
|---|---|---|---|---|---|
| CZ4.1 | 2024-H2 | bull | 13 → 6 | -1.31 → **+0.09** | rescue (evita perda) |
| CZ4.2 | 2025-H1 | chop | 17 → 6 | 0.64 → 0.66 | neutro |
| CZ4.3 | 2025-H2 | misto | 23 → 7 | **2.81 → 0.46** | **destruição** |

## Interpretação

Filter trend_htf(1d, sma=20, short_only) corta ~60% dos trades em todas janelas. Resultado assimétrico:
- **bull 2024-H2**: filter evita a maioria dos shorts em tendência altista → transforma -1.31 em +0.09 (rescue esperado)
- **chop 2025-H1**: regime já favorável ao short; filter reduz n mas preserva Sharpe (neutro)
- **misto 2025-H2**: filter corta justamente os melhores shorts (contra-tendência curta) → colapso 2.81 → 0.46

Padrão 28 aplicado: a receita de v6 (trend_htf 4h sobre base 1h rescuing short) **não transporta para 4h base**. A relação entre HTF e LTF muda a seletividade do filter — em base 4h com htf=1d, o HTF é "muito rápido" relativo ao LTF (só 6 barras) e invalida trades bons.

## Decisão

**trend_htf(1d) rejeitado como rescue em 4h.** Gate pré-registrado (ADR-0120):
1. Promoção v9-4h-filtered: 0/3 strict + degradação em 2/3 → **REFUTADO**
2. Salvamento contextual (3/3 Sh≥0.3): 2/3 (CZ4.1 ficou 0.09) → **parcial**

Staging CZ2 permanece inalterado. SOL 4h RSI short continua staging/contextual sem filter viável identificado.

## Padrão 31 (NOVO): transposição de filter HTF entre timeframes é não-linear

trend_htf requer ratio HTF/LTF suficiente pra capturar tendência macro sem cortar trades de contra-tendência. V6 em 1h usou 4h×20 = 80 barras 1h ≈ 13 dias. Em 4h, equivalente seria HTF com janela 80 barras 4h = 13 dias → htf=1d:sma=13 (não 1d:sma=20).

Proposta futura: se retestar SOL 4h com filter, usar sma=13 em htf=1d (equivalente temporal ao v6) OU htf=1W (mesma escala semanal).

Não testar agora — manter CZ4 refutado e seguir backlog.

## Follow-up aberto

1. CZ4b (não agendado): SOL 4h + trend_htf(1W, sma=4) — HTF semanal, sma curta
2. CZ4c (não agendado): SOL 4h + bollinger_width (filter de regime em vez de direcional)

## Ação executada

- ✅ ADR-0121 closeout
- ✅ Série CZ4 documentada
- ✅ STATE.md entry (consolidado CZ4+CZ5+CZ6)

## Não-alvo

- Não criar manifest v9-4h-filtered (gate refutado)
- Não alterar stack
- Não emitir bridge

## Stack pós-CZ4

13 combos inalterados.
