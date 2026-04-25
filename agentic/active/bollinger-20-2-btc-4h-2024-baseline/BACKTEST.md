# BACKTEST.md — M.2 Bollinger 20/2 BTC 4h 2024

## Dataset

`btcusdt_4h_20240705_20241231_binance_spot` — 1080 barras 4h, sha256=`2b1256ea`.

## Métricas

### Baseline

| métrica      | valor    |
| ------------ | -------- |
| final_equity | 9932.49  |
| hit_rate     | 52.63%   |
| total_trades | 19       |
| max_drawdown | 4.38%    |

**Fe baseline marginal** (−0.68% do capital) — essencialmente breakeven.

### Stress

| scenario  | fe      | hit    | Δ fe    | ratio |
| --------- | ------- | ------ | ------- | ----- |
| baseline  | 9932.49 | 52.63% | —       | 1.000 |
| fee+10    | 9856.70 | 52.63% | −0.76%  | 0.9924 |
| slip+5    | 9924.90 | 52.63% | −0.08%  | 0.9992 |
| spread+10 | 9856.70 | 52.63% | −0.76%  | 0.9924 |

### WF (4 folds)

| fold | trades | hit    |
| ---- | ------ | ------ |
| 1    | 4      | 75.00% |
| 2    | 2      | 50.00% |
| 3    | 2      | 0.00%  |
| 4    | 5      | 40.00% |

**2/4 folds cruzam 45%.** Alta variância entre folds (0-75%) por amostra mínima.

### MC (500, seed=42)

p5=9605.22 | p50=9966.14 | p95=10252.38

p50 < 10000 e p95 apenas ligeiramente > 10000 — distribuição centrada em breakeven.
