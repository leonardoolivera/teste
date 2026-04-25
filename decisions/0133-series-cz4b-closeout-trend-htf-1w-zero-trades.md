# 0133 — Série CZ4b closeout: trend_htf(1W,4) zero trades, Padrão 31 corolário refutado

**Status:** Accepted — filter inviável, trend_htf em 4h fechado por enquanto
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0132 (pré-reg), ADR-0121 (CZ4 1d falhou), Padrão 31

## Resultado

| Tag | Janela | Trades |
|---|---|---:|
| CZ4b.1 | 2024-H2 bull | **0** |
| CZ4b.2 | 2025-H1 chop | **0** |
| CZ4b.3 | 2025-H2 misto | **0** |

**0 trades em todas as janelas.** Filter zerou o universo de entrada.

## Interpretação

trend_htf(1W, sma=4, short_only) requer que close semanal atual esteja abaixo de SMA(4) semanais. Numa janela 6-month de SOL, isso quase nunca acontece de forma sustentada o suficiente pra coincidir com sinal RSI overbought 4h — produz 0 ativações úteis.

Padrão 31 corolário hipotetizou que ratio temporal HTF/LTF correto preservaria o filter. Resultado mostra que **distribuição estatística do filter** depende não só do ratio temporal mas também da **granularidade da SMA HTF** — sma=4 weekly tem só ~4 atualizações/mês, gerando estados booleanos muito esparsos.

## Decisão

**trend_htf em 4h fechado por enquanto.** CZ4 (1d,20) destruiu edge; CZ4b (1W,4) zerou universo. Variantes intermediárias possíveis (1d,13 ou 1W,8) têm baixa prior de produzir resultado diferente — sma curta rara ativa, sma longa lag composto.

Padrão 31 mantém-se como observação válida (HTF/LTF transposição é não-linear) mas o **corolário "ratio equivalente preserva filter"** é REFUTADO. Não há receita simples pra transportar trend_htf de 1h pra 4h.

## Implicação para SOL/ETH 4h staging

CZ2 + CZ5 ETH staging permanecem **sem filter direcional viável**. Promoção a manifest v9-4h fica condicionada a:
1. 3ª janela strict (bloqueada por dataset SOL 2024-H1 ausente)
2. Engine diferente em 4h (não testado)
3. Decisão explícita do usuário pra promoção sob protocolo relaxado

## Padrão 37 (NOVO): granularidade SMA HTF afeta distribuição estatística do filter

trend_htf não é só lag — é também estado booleano cuja **frequência de mudança** depende de (a) timeframe HTF e (b) janela SMA. Combinações com SMA curta + HTF longo geram estados esparsos (filter raramente ativa); SMA longa + HTF longo geram lag composto.

Sweet spot empírico observado em v6 (1h base + HTF=4h + sma=20): HTF é ~4× LTF, SMA cobre ~80 barras LTF (~3 dias). Em 4h base, equivalente seria HTF=4h-sem-resample (já LTF) ou 16h (não suportado pelo engine).

Conclusão: **trend_htf canônico não tem variante viável em 4h base** — sweet spot exigiria HTF intermediário (8h, 16h) que o engine atual não expõe (`_ALLOWED_HTF = ("4h", "1d", "1W")`).

## Próximo possível (não agendado)

1. Adicionar HTF intermediários ao engine (8h, 16h) — trabalho de código
2. Filter alternativo pra 4h: regime ADX, ATR ratio, vol-percentile, TWAP slope — nenhum implementado hoje
3. Aceitar que SOL/ETH 4h staging permanece sem filter viável e seguir

## Ação executada

- ✅ ADR-0133 closeout
- ✅ Série CZ4b documentada
- ✅ STATE.md entry (consolidado tarde-3)

## Não-alvo

- Não testar mais variantes trend_htf 4h
- Não promover SOL/ETH 4h staging
- Não alterar stack

## Stack pós-CZ4b

13 combos inalterados.
