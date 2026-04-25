# BACKTEST.md — J.2 Bollinger 20/2 BTC 180d 2024

## Dataset

`btcusdt_1h_20240705_20241231_binance_spot` — BTCUSDT 1h, 4320 barras, sha256=`64819bcf`.

## Métricas

### Baseline

| métrica      | valor    |
| ------------ | -------- |
| final_equity | 10252.14 |
| hit_rate     | **68.24%** |
| total_trades | 85       |
| max_drawdown | 3.62%    |

### Stress

| scenario  | fe       | hit    | Δ fe   |
| --------- | -------- | ------ | ------ |
| baseline  | 10252.14 | 68.24% | —      |
| fee+10    | 9911.98  | 57.65% | −3.32% |
| slip+5    | 10218.06 | 67.06% | −0.33% |
| spread+10 | 9911.98  | 57.65% | −3.32% |

### WF (4 folds)

| fold | fe       | hit    | trades |
| ---- | -------- | ------ | ------ |
| 1    | 10038.19 | 71.43% | 14     |
| 2    | 10016.78 | 64.71% | 17     |
| 3    | 9986.85  | 71.43% | 14     |
| 4    | 10191.47 | 72.73% | 22     |

**4/4 folds cruzam 45% com margem larga (64.71% é o menor).** Fold_std_hit = 3.48 pp — **homogeneidade máxima do protocolo**.

### MC (500, seed=42)

p5=9921.73 | p50=10327.83 | p95=10686.20

## Cross-window BTC (I.2 2025 vs J.2 2024)

| janela      | fe       | hit    | trades | mdd   | fold_min |
| ----------- | -------- | ------ | ------ | ----- | -------- |
| I.2 2025-H2 | 10033.00 | 65.85% | 82     | 2.80% | 44.44%   |
| **J.2 2024-H2** | **10252.14** | **68.24%** | **85** | 3.62% | **64.71%** |

**J.2 > I.2 em hit, fe e fold-min.** Fold-min sobe de 44.44% (marginal) para 64.71% (folgado).
