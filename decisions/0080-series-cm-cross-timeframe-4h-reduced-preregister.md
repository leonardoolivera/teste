# 0080 — Série CM: cross-timeframe 4h escopo reduzido (3 pilotos 2024-H2) — pré-registro

**Status:** Accepted — pré-registro escopo reduzido; execução autorizada
**Date:** 2026-04-19
**Deciders:** Usuário + agente
**Relates to:** ADR-0077 (CL closeout — Padrão 16), ADR-0069 (v4a/v4b ativos), ADR-0062 (CH closeout)

## Contexto

Série CL (ADR-0077) confirmou v4 é threshold-específico. Pergunta de **generalidade** restante: o edge é específico ao timeframe 1h ou estrutural ao regime? CM testa esta segunda dimensão.

**Bloqueador descoberto na execução:** apenas BTC/ETH/SOL **2024-H2** têm dataset 4h processado. Demais janelas (2024-H1, 2025-H1, 2025-H2) ausentes. Sem tooling de ingest disponível.

**Decisão de escopo:** rodar versão reduzida (3 pilotos = BTC/ETH/SOL × 2024-H2 4h) ciente da limitação. Resultado tem valor parcial: testa **uma janela** cross-timeframe; se PASS aponta hipótese estrutural válida (justifica ingerir mais janelas); se FAIL refuta cross-timeframe pra essa janela específica (pode ser regime ou pode ser timeframe — confounded).

## Decisão

3 pilotos 4h × 3 ativos × janela 2024-H2, com params v4b (RSI 14/30/70 puro, sem filter) — manifest mais simples. Justificativa: v4b PASS sem filter em 2025-H2 1h é o **edge mais limpo** do stack; testar generalidade sem confound de regime filter.

### Matriz (3 pilotos 4h)

- CM.1 — BTC 2024-H2 4h
- CM.2 — ETH 2024-H2 4h
- CM.3 — SOL 2024-H2 4h

### Parâmetros de engine

- capital 10000, fracao 0.1, alavancagem 2.0, `--sizing-mode fixed_notional`
- taker 5bps, slippage 2bps, spread 0
- strategy rsi, period=14, oversold=30, overbought=70, `--no-long-only`
- **filter: none** (espelho v4b)
- n-folds 5, rolling, train_fraction 0.5, min_test_bars 50
- mc_resamples 1000, mc_seed 42
- stress `fee+10:10:0:0`, `spread+10:0:0:10`

### Gates pré-registrados (ajustados ao escopo reduzido)

- **Gate 1 — principal (relaxado):** ≥ **1/3** PASS critério manifest. Justificativa: amostra é 1/3 do espelho 9-pilotos; ≥1 PASS já indica sinal cross-timeframe digno de investimento em ingest pra demais janelas.
- **Gate 2 — trade count:** ≥ **2/3** com trades ≥ 30. Risco real: 4h tem 1/4 das barras → janela 2024-H2 4h ~1100 barras vs 4400 em 1h. Trade count cai proporcionalmente.
- **Gate 3 — cross-timeframe lift comparativo:** Sharpe 4h ≥ Sharpe 1h equivalente em ≥1/3 pilotos.
  - BTC 2024-H2 1h sem filter (referência: CG.1 Sh ~0.9 baseline ou v4b BTC 2025-H2 Sh=1.64)
  - SOL 2024-H2 1h sem filter (CK.1 Sh=−1.02, CH.3 width Sh=−0.39)
  - ETH 2024-H2 1h: similar BTC/SOL na ordem
- **Gate 4 — Padrão 16 prevenção:** se CM PASS, **não promover diretamente** — CM é janela única, sample insuficiente para manifest novo. PASS = autorizar próxima série CM-completo (com ingest de 2024-H1, 2025-H1, 2025-H2 4h).

## Hipóteses explícitas

1. **H-edge-estrutural-cross-timeframe** (CM PASS ≥1/3 com trades≥30): edge RSI mean-rev short generaliza para 4h. Justifica ingerir restante das janelas 4h.
2. **H-edge-1h-específico** (CM FAIL 0/3 ou trade count colapsa): edge é específico à granularidade horária — provavelmente porque mean-rev em 4h tem pulses muito mais raros e horizon de exit maior. Refuta cross-timeframe sem ingerir mais.
3. **H-confound-regime** (CM mixed: SOL PASS, BTC/ETH FAIL): replicaria padrão 14 (SOL especial) também em 4h → reforça hipótese asset-específica, não timeframe-específica.

## Saída da série

- **H-edge-estrutural PASS:** documentar PASS, ABRIR pendência "ingerir 2024-H1+2025-H1+2025-H2 4h" para futura sessão CM-completo (não auto-execução).
- **H-edge-1h-específico FAIL:** documenta limitação clara — v4 stack é 1h-específico. Não impede uso, apenas escopo. Padrão 18 candidato sobre escopo de timeframe.
- **H-confound-regime mixed:** confirma Padrão 14 (asset-específico mais forte que timeframe), abre track CM-SOL-only.

## Tooling

- `tools/run_cm_sweep.py`: 3 runs, run_id `cm-rsi-pure-<asset>-20240705_20241231-4h-short`

## Timebox

~5min compute (3 runs com poucas barras) + ADR-0081 closeout mesmo turno.

## Critério de sucesso desta ADR

1. 3 runs executam sem crash
2. Métricas extraídas e gates avaliados
3. ADR-0081 emitida com decisão (PASS abre pendência ingest, FAIL arquiva)
