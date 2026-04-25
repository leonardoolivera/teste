# BACKTEST.md — H.6 Donchian + Composite(sma OR atr)

## Dataset

`btcusdt_1h_20250705_20251231_binance_spot` — BTCUSDT 1h, 4320 barras, `declared_gaps: []`. Idêntico a H.1/H.3/H.4/H.5.

## Métricas

### Baseline cost_stress

| métrica      | valor   |
| ------------ | ------- |
| final_equity | 9128.87 |
| hit_rate     | 26.79%  |
| total_trades | 112     |
| max_drawdown | 10.26%  |

### Stress scenarios

| scenario  | fe      | hit    | trades | mdd    | Δ fe    |
| --------- | ------- | ------ | ------ | ------ | ------- |
| baseline  | 9128.87 | 26.79% | 112    | 10.26% | —       |
| fee+10    | 8683.06 | 20.54% | 112    | 14.48% | −4.89%  |
| slip+5    | 9084.32 | 25.89% | 112    | 10.68% | −0.49%  |
| spread+10 | 8683.06 | 20.54% | 112    | 14.48% | −4.89%  |

`spread+10 / baseline = 0.9511` — critério 3 passa por margem estreita (0.0011 acima do piso; menor folga do protocolo).

### Walk-forward (4 folds)

| fold | fe       | hit    | trades | mdd   |
| ---- | -------- | ------ | ------ | ----- |
| 0    | 9830.90  | 22.73% | 22     | 2.06% |
| 1    | 10017.28 | 36.84% | 19     | 0.92% |
| 2    | 9762.13  | 30.00% | 20     | 3.18% |
| 3    | 9747.56  | 25.00% | 24     | 4.39% |

Fold 1 é o **único fold com final_equity > capital inicial do protocolo** (10017.28). Nenhum fold cruza 45%.

### Monte Carlo (500 resamples, seed=42)

| p  | fe      | mdd    |
| -- | ------- | ------ |
| 5  | 8973.85 | 3.52%  |
| 50 | 9363.75 | 6.96%  |
| 95 | 9827.94 | 10.54% |

## Quadro consolidado (H.1, H.3, H.4, H.5, H.6)

| piloto | filter               | fe      | hit    | trades | mdd    |
| ------ | -------------------- | ------- | ------ | ------ | ------ |
| H.1    | none                 | 9089.79 | 25.45% | 110    | 10.49% |
| H.3    | sma_slope            | 9195.59 | 29.82% | 114    | 9.60%  |
| H.4    | atr_regime           | 9180.45 | 26.39% | 72     | 8.80%  |
| H.5    | and(sma, atr)        | 9247.34 | 29.73% | 74     | 8.14%  |
| **H.6**| **or(sma, atr)**     |**9128.87**|**26.79%**|**112**|**10.26%**|

- OR produz o piloto mais próximo de H.1 em todas as métricas — **coerente** com OR ser a composição mais permissiva (aceita quase tudo que qualquer filtro aceita).
- `trade_count=112` fica entre H.1 (110) e H.3 (114) — OR não é mais permissivo que cada individual sobre o período inteiro devido à fragmentação inversa (trades consolidam em trades longos).

## Compare H.5 ↔ H.6

- flags diff: `regime_filter` (`and(...)` → `or(...)`), `run_id` — **exatamente 2**.
- trades: 74 → 112 (+38, +51%).
- fe: 9247.34 → 9128.87 (Δ=−118.47).
- hit: 29.73% → 26.79% (Δ=−2.94 pp).
- mdd: 8.14% → 10.26% (Δ=+2.12 pp).

OR piora toda métrica direcional vs AND. Assinatura: AND concentra em regimes simultaneamente bons (poucos trades, hit estável); OR dilui com regimes-menos-bons (muitos trades, hit degrada).
