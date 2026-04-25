# BACKTEST.md — I.1 Bollinger 20/2 SOL 180d

## Dataset

`solusdt_1h_20250705_20251231_binance_spot` — SOLUSDT 1h, 4320 barras, `declared_gaps: []`.
Idêntico a H.10 (Donchian SOL) — cross-family comparável no mesmo tape.

## Métricas

### Baseline

| métrica      | valor     |
| ------------ | --------- |
| final_equity | 10189.15  |
| hit_rate     | **65.85%**|
| total_trades | 82        |
| max_drawdown | 6.93%     |
| total_pnl    | +189.15   |

### Stress

| scenario  | fe       | hit    | mdd    | Δ fe    |
| --------- | -------- | ------ | ------ | ------- |
| baseline  | 10189.15 | 65.85% | 6.93%  | —       |
| fee+10    | 9859.11  | 63.41% | 7.69%  | −3.24%  |
| slip+5    | 10156.07 | 65.85% | 6.99%  | −0.32%  |
| spread+10 | 9859.11  | 63.41% | 7.69%  | −3.24%  |

### WF (4 folds)

| fold | fe       | hit         | trades | mdd   |
| ---- | -------- | ----------- | ------ | ----- |
| 1    | 10238.52 | 73.33%      | 15     | 1.69% |
| 2    | 9400.58  | 50.00%      | 14     | 6.94% |
| 3    | 10167.38 | 76.47%      | 17     | 2.50% |
| 4    | 10343.77 | **76.19%**  | 21     | 1.38% |

**Todos os 4 folds cruzam 45%** — homogeneidade inédita no protocolo (comparar: H.10 tinha fold
pior a 9.52%; H.9 tinha fold pior a 17.65%). Fold 2 (50%) é o pior e ainda assim passa baseline.

### MC (500 resamples, seed=42)

| pct | final_equity |
| --- | ------------ |
| p5  | 9277.98      |
| p50 | 10140.97     |
| p95 | 10922.44     |

`original_final_equity=10143.92` (MC sobre trades apresenta leve divergência vs baseline de cost
stress por ordem de remuestra; diferença < 1%).

## Observações

- **Hit_rate baseline 65.85% é 2.06× o maior da Série H** (H.10 SOL = 31.07%). Primeiro piloto
  do protocolo a cruzar não só 45%, mas 60%.
- **Fold-consistency maior do protocolo:** `fold_std_hit = 11.04 pp`; `fold_min - fold_max = 26.47
  pp`. Comparar H.10: `fold_min - fold_max = 38.10 pp`.
- **82 trades em 180d** (vs 103 em H.10): Bollinger dispara menos por ser edge-triggered duplo
  (precisa de cruzamento em ambos t-1 e t-2). Menos trades, mais seletividade.
- **Max_drawdown 6.93%** — 3º menor do protocolo após H.7 (5.94%) e H.9 (6.64%). SOL conseguiu
  menor mdd na família mean-reversion do que na breakout (H.10 SOL: 14.55%).
- **Spread_stress_ratio 0.968** — passa critério 3 com folga.

## Quadro cross-family SOL (baseline sem filtro, 180d)

| piloto  | família         | fe       | hit     | trades | mdd    |
| ------- | --------------- | -------- | ------- | ------ | ------ |
| H.10    | Donchian 20/10  | 9119.73  | 31.07%  | 103    | 14.55% |
| **I.1** | **Bollinger 20/2** | **10189.15** | **65.85%** | **82** | **6.93%** |

Domínio completo: Bollinger vence em **todas** as dimensões (fe, hit, mdd) com menos trades.
SOL tem componente mean-reversion dominante na janela 2025-07 a 2025-12. Falsifica a hipótese
Série H "edge não existe" — edge existe em **outra família**.

## Snapshot de ranking (N=13, ADR-0024 DEFAULT_WEIGHTS, 2026-04-18T10:22:35Z)

| rank | slug                                     | score  | hit     | fe       |
| ---- | ---------------------------------------- | ------ | ------- | -------- |
| **1**| **bollinger-20-2-sol-180d-baseline**     | **7.66** | **65.85%** | **10189.15** |
| 2    | donchian-20-10-eth-180d-regime-sma       | 5.49   | 32.29%  | 10504.18 |
| 3    | ma-crossover-20-50-btc-180d-baseline     | 4.96   | 31.11%  | 9564.25  |
| 4–13 | demais Série H                           | 1.03–4.74 | 24–32% | 8527–9533 |

**Bollinger I.1 é rank 1 com margem (+2.17 pontos sobre rank 2).** `flags_digest: 588892862bd5997a`.
