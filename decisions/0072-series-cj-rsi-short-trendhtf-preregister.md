# 0072 — Série CJ: RSI short + TrendHTF(4h, sma=50, short_only) (pré-registro)

**Status:** Accepted — pré-registro; execução autorizada
**Date:** 2026-04-19
**Deciders:** Usuário + agente
**Relates to:** ADR-0062 (CH closeout PASS RSI+width), ADR-0068 (Padrão 12 regime-específico), ADR-0071 (CI closeout FAIL Donchian+width, Padrão 13 payoff-direction-específico), ADR-0046/0047 (CD Donchian+TrendHTF closeout)

## Contexto

Padrão 13 (ADR-0071): filter precisa alinhar com direção do edge. CH (RSI+width) PASS 4/9 com 5 FAILs concentrados em 2024-H2 bull (CH.1/2/3 BTC/ETH/SOL Sharpe negativo). Hipótese de gap: width filtra **regime de volatilidade**, mas não **direção de tendência**. Em 2024-H2 bull, ambientes secos ainda têm bias direcional pra cima — RSI short entra contra trend e perde.

**TrendHTF short_only** (ADR-0043) é filter direcional puro: ativa apenas quando close HTF < SMA HTF (downtrend confirmado em timeframe maior). Composição com RSI short:
- Em uptrend HTF: filter desliga sinais → zero trades short erroneamente against-trend
- Em downtrend HTF: filter habilita → RSI short opera normalmente, capturando reversões dentro do downtrend

Se hipótese válida, CJ deve **passar onde CH falhou** (2024-H2 bull) e **não estragar onde CH passou** (2025-H1 chop, 2025-H2 misto que tinham downtrend parcial).

## Diferenciação vs séries anteriores

- **vs CH (RSI+width):** troca filter de volatilidade por filter direcional. Mesma família, mesma direção.
- **vs CD (Donchian+TrendHTF):** CD testou TrendHTF com breakout long. Falhou (ADR-0047) — esperado por Padrão 13 invertido (TrendHTF direcional fez breakout reverter de "rompe pra cima" pra ambiente acumulação). CJ testa direção alinhada (short + downtrend), não conflitante.

## Decisão

Espelhar CH com troca de filter. Mesmos 9 pilotos, mesmos params engine. Delta único: `--regime-filter trend_htf:htf=4h:sma_window=50:mode=short_only` em vez de `bollinger_width`.

### Matriz de pilotos (idêntica CG/CH/CI)

9 pilotos: BTC/ETH/SOL × 2024-H2/2025-H1/2025-H2.

| Tag | Asset | Window |
|---|---|---|
| CJ.1 | BTC | 2024-H2 |
| CJ.2 | ETH | 2024-H2 |
| CJ.3 | SOL | 2024-H2 |
| CJ.4 | BTC | 2025-H1 |
| CJ.5 | ETH | 2025-H1 |
| CJ.6 | SOL | 2025-H1 |
| CJ.7 | BTC | 2025-H2 |
| CJ.8 | ETH | 2025-H2 |
| CJ.9 | SOL | 2025-H2 |

### Parâmetros de engine (idênticos CH)

- capital 10000, fracao 0.1, alavancagem 2.0, `--sizing-mode fixed_notional`
- taker 5bps, slippage 2bps, spread 0
- strategy rsi, period=14, oversold=30, overbought=70, `--no-long-only`
- filter `trend_htf:htf=4h:sma_window=50:mode=short_only`
- n-folds 5, rolling, train_fraction 0.5, min_test_bars 50
- mc_resamples 1000, mc_seed 42
- stress `fee+10:10:0:0`, `spread+10:0:0:10`

### Gates pré-registrados

- **Gate 1 — principal**: ≥ **3/9** PASS critério manifest (trades≥30, Sharpe≥1.0, MDD≤20, MCp5>9500, cost_r≥0.95)
- **Gate 2 — recuperação 2024-H2** (específico desta série): em 2024-H2 (3 pilotos), CJ tem **≥1/3 PASS** vs CH 0/3. Se TrendHTF não recupera nenhum 2024-H2, hipótese refutada.
- **Gate 3 — não-degradação 2025-H1+H2**: em 2025-H1+H2 (6 pilotos), CJ tem **≥3/6 PASS** (mantém ou melhora vs CH 4/6). Se filter direcional reduz trade count em chop sem ganho de Sharpe, é cost trade-off líquido negativo.
- **Gate 4 — trade count mínimo viável**: ≥6/9 pilotos com trades≥30. TrendHTF é gate restritivo; pode zerar trade count em alguns combos.
- **Gate 5 — audit Gate B (Padrão 12)**: se Gate 1 PASS e ≥1 PASS em janela CH-FAIL, audit obrigatório re-rodando esses combos sem filter para confirmar load-bearing.

### Regras anti-movimento

Gates fixos. Não renegociáveis. Combinatória mínima pra promoção: Gate 1 + Gate 2 + Gate 5. Se Gate 1 PASS mas Gate 2 FAIL (passou só onde CH já passava), arquiva como "TrendHTF não adiciona valor — width já era suficiente".

## Hipóteses explícitas

1. **H-direcional-recupera** (Gate 2 PASS, ≥1/3 em 2024-H2): TrendHTF resgata 2024-H2 bloqueando entries contra trend HTF. Pelo menos 1 dos BTC/ETH/SOL 2024-H2 vira PASS.
2. **H-direcional-redundante** (Gate 1 PASS mas Gate 2 FAIL): TrendHTF preserva o que CH já passava (2025-H1 + 2025-H2) mas não adiciona novo. Filter direcional é caro em trade count sem trazer combos novos.
3. **H-direcional-quebra** (Gate 1 FAIL ou Gate 4 FAIL): TrendHTF é restritivo demais — zera trade count em chop ou bloqueia entries que de fato eram boas. Refuta uso de TrendHTF com mean-rev short.

## Alternativas consideradas

### htf=1d em vez de 4h
Rejeitado por ora. 1d é mais lento; em janelas semestrais tem ~180 candles 1d, SMA(50) deixa só 130 candles ativos efetivos. 4h dá ~1080 candles, SMA(50) ainda permite filter responsivo. Se CJ passar com 4h, 1d vira teste adicional.

### sma_window diferente de 50
Rejeitado. 50 é convenção tradicional (SMA50 de 1d ≈ 200 períodos 4h ≈ análogo SMA200 1d-trader). Variar quebra falsificabilidade.

### Composição AND com width 300
Rejeitado nesta série. Quero testar TrendHTF puro vs width puro pra atribuir efeito. Se ambos passarem isolados, composição AND vira ADR futura.

### Volume filter
Rejeitado por implementação faltante. AF não tem `VolumeFilter` — exigiria desenvolvimento + testes antes de série. Reservado pra depois se TrendHTF abrir caminho.

## Saída da série

- **Gate 1 PASS + Gate 2 PASS + Gate 5 PASS:** elegível para manifest v5 via ADR de promoção (espelho ADR-0058). Combos PASS expandem cobertura cross-período além de v4a/v4b.
- **Gate 1 PASS + Gate 2 FAIL (H-redundante):** documenta TrendHTF não-aditivo vs width. Não promove.
- **Gate 1 FAIL ou Gate 4 FAIL (H-quebra):** TrendHTF não compõe com mean-rev short no formato testado. Padrão 14 candidato: filter direcional HTF em timeframe muito superior degrada trade frequency abaixo do gate em chop.

## Tooling

- `tools/run_cj_sweep.py`: 9 runs, run_id `cj-rsi-14-30-70-<asset>-<suffix>-trendhtf-4h-50-short`

## Timebox

~15-20min compute + ADR-0073 closeout mesmo dia.

## Critério de sucesso desta ADR

1. 9 runs executam sem crash (TrendHTF requer DatetimeIndex; precisa validar dataset)
2. Métricas extraídas e gates avaliados
3. ADR-0073 emitida com decisão
