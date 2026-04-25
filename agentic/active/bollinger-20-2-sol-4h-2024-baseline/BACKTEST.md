# BACKTEST.md — M.1 Bollinger 20/2 SOL 4h 2024

## Dataset

`solusdt_4h_20240705_20241231_binance_spot` — 1080 barras 4h, sha256=`04a5a335`.

## Métricas

### Baseline

| métrica      | valor    |
| ------------ | -------- |
| final_equity | 9766.99  |
| hit_rate     | 57.14%   |
| total_trades | 21       |
| max_drawdown | 6.99%    |

**Fe baseline < capital inicial (−2.33%)** — edge não cobre custos mesmo em 4h.

### Stress

| scenario  | fe      | hit    | Δ fe    | ratio |
| --------- | ------- | ------ | ------- | ----- |
| baseline  | 9766.99 | 57.14% | —       | 1.000 |
| fee+10    | 9683.54 | 57.14% | −0.85%  | 0.9915 |
| slip+5    | 9758.64 | 57.14% | −0.09%  | 0.9991 |
| spread+10 | 9683.54 | 57.14% | −0.85%  | 0.9915 |

**Sensibilidade a custos é ~15× menor que em 15m** (L.1: Δ=−12.90%; M.1: Δ=−0.85%).
Apenas 21 trades vs 336 em 15m ≈ mesma razão 1:16.

### WF (4 folds)

| fold | trades | hit    |
| ---- | ------ | ------ |
| 1    | 3      | 33.33% |
| 2    | 5      | 60.00% |
| 3    | 1      | 0.00%  |
| 4    | 6      | 66.67% |

**Apenas 2/4 folds cruzam 45%.** Fold 3 tem 1 trade → hit 0% domina métrica. Amostra insuficiente.

### MC (500, seed=42)

p5=9300.91 | p50=9931.68 | p95=10457.43

**p5 e p50 abaixo de 10000** — Monte Carlo confirma que edge econômico não existe; p95 apenas
roça breakeven.

## Comparação M.1 4h vs J.1 1h vs L.1 15m (SOL, mesma janela)

| métrica | M.1 (4h) | J.1 (1h) | L.1 (15m) |
|---------|----------|----------|-----------|
| barras | 1080 | 4320 | 17280 |
| trades | 21 | 87 | 336 |
| hit | 57.14% | 67.82% | 63.10% |
| fe baseline | 9766.99 | 10684.24 | 10433.99 |
| spread+10 ratio | **0.9915** | 0.967 | 0.871 |
| Δ fee+10 | −0.85% | −3.27% | −12.90% |
| critério 3 | **OK** | OK | **VIOLADO** |
| critério 1 baseline | OK | OK | OK |
| fe > capital? | **NÃO** | SIM | SIM |
| release | fail | canary_only | fail |

**1h é o sweet spot.** 15m quebra por custos, 4h quebra por amostra/edge insuficiente.
