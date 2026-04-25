# 0076 — Série CL: RSI(9/25/75) short cross-period (pré-registro)

**Status:** Accepted — pré-registro; execução autorizada
**Date:** 2026-04-19
**Deciders:** Usuário + agente
**Relates to:** ADR-0062 (CH closeout PASS RSI 14/30/70+width), ADR-0069 (v4a/v4b ativos), ADR-0075 (CK closeout Padrão 15)

## Contexto

V4a (RSI 14/30/70 + width 300) e v4b (RSI 14/30/70 sem filter) ativos. Pergunta de robustez: o edge é ao **family RSI mean-rev** ou **a essa configuração específica de thresholds**? Padrão 15 (ADR-0075) reforça preocupação com edge fantasma — variar thresholds testa se Sharpe v4b SOL 2.30 é estrutural ou overfit ao corte 30/70.

Thresholds **9/25/75**: RSI mais curto (9 períodos = mais sensível) + thresholds mais extremos (25/75 = só dispara em condições mais raras). Hipótese de literatura: RSI 9 detecta reversões mais cedo; thresholds 25/75 reduzem falsos positivos vs 30/70. Composição opera em direção oposta — cancela ou amplifica?

## Decisão

Espelhar CH no formato (9 pilotos cross-period, mesma DS, mesma engine), variando apenas RSI params:
- `--rsi-period 9` (vs 14)
- `--rsi-oversold 25` (vs 30)
- `--rsi-overbought 75` (vs 70)

Filter: **width 300** (espelho CH/v4a). Decisão pragmática: usar mesmo filter que validou CH, isolando o efeito dos thresholds. Versão sem filter (espelho v4b) fica pra ADR adicional se CL com filter passar.

### Matriz de pilotos (idêntica CG/CH/CI/CJ)

9 pilotos: BTC/ETH/SOL × 2024-H2/2025-H1/2025-H2.

### Parâmetros de engine

- capital 10000, fracao 0.1, alavancagem 2.0, `--sizing-mode fixed_notional`
- taker 5bps, slippage 2bps, spread 0
- strategy rsi, **period=9, oversold=25, overbought=75**, `--no-long-only`
- filter `bollinger_width:window=30:num_std=1.5:min_width_bps=300`
- n-folds 5, rolling, train_fraction 0.5, min_test_bars 50
- mc_resamples 1000, mc_seed 42
- stress `fee+10:10:0:0`, `spread+10:0:0:10`

### Gates pré-registrados

- **Gate 1 — principal:** ≥ **3/9** PASS critério manifest
- **Gate 2 — robustez vs CH:** em ≥ **3/9** pilotos, CL Sh **dentro de ±25%** de CH Sh (mantém edge sem mover muito). Se CL é radicalmente diferente, edge é threshold-específico.
- **Gate 3 — não-degradação trade count:** ≥ **6/9** com trades ≥ 30. Thresholds 25/75 podem zerar trade count (sinais raros).
- **Gate 4 — audit Gate B:** se Gate 1 PASS, audit obrigatório (re-rodar combos PASS sem filter — Padrão 12).
- **Gate 5 — Padrão 15 prevenção:** lift vs CH não pode ser único critério. Se CL passa só onde CH passa, é redundância. Se CL passa **onde CH falha** (gap recovery, principalmente 2024-H2), é sinal estrutural distinto digno de promoção via Padrão 12.

## Hipóteses explícitas

1. **H-overfit-thresholds** (CL FAIL ≤2/9): edge v4 é específico ao 14/30/70. Thresholds 9/25/75 destroem. Justifica não-expansão de manifest pra outros thresholds.
2. **H-robusto-cross-thresholds** (CL PASS 3-5/9 com Sh ±25% de CH): edge é estrutural RSI mean-rev short + width; thresholds são ajuste fino. Confirma robustez de v4.
3. **H-thresholds-importam-mas-diferente** (CL PASS em janelas distintas de CH): RSI 9 captura janelas curtas onde RSI 14 perde; gap recovery 2024-H2 possível. Abre track v5 RSI-9 paralelo.

## Saída da série

- **Gate 1 + 2 PASS (H-robusto):** confirma robustez v4. Documenta sem promoção (v4 já cobre). Padrão 16 candidato: "RSI mean-rev short + width 300 é robusto a perturbação ±50% nos thresholds (14→9, 30→25, 70→75)".
- **Gate 1 PASS + 5 PASS (H-thresholds-distinto):** abre ADR de promoção pra manifest v5 RSI-9 escopado às janelas onde CL bate CH.
- **Gate 1 FAIL (H-overfit):** v4 é threshold-específico. Documenta limitação; manifest v4 mantém escopo restrito ao 14/30/70.

## Tooling

- `tools/run_cl_sweep.py`: 9 runs, run_id `cl-rsi-9-25-75-<asset>-<suffix>-width30-300-short`

## Timebox

~15-20min compute + ADR-0077 closeout mesmo turno.

## Critério de sucesso desta ADR

1. 9 runs executam sem crash
2. Métricas extraídas e gates avaliados
3. ADR-0077 emitida com decisão
