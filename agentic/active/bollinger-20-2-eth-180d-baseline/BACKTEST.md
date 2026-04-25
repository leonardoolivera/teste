# BACKTEST.md — I.3 Bollinger 20/2 ETH 180d

## Dataset

`ethusdt_1h_20250705_20251231_binance_spot` — ETHUSDT 1h, 4320 barras.

## Métricas

### Baseline

| métrica      | valor    |
| ------------ | -------- |
| final_equity | 10057.17 |
| hit_rate     | **63.41%** |
| total_trades | 82       |
| max_drawdown | 5.17%    |

### Stress

| scenario  | fe       | hit    | mdd   | Δ fe   |
| --------- | -------- | ------ | ----- | ------ |
| baseline  | 10057.17 | 63.41% | 5.17% | —      |
| fee+10    | 9729.39  | 59.76% | 6.89% | −3.26% |
| slip+5    | 10024.34 | 63.41% | 5.31% | −0.33% |
| spread+10 | 9729.39  | 59.76% | 6.89% | −3.26% |

### WF (4 folds)

| fold | fe       | hit    | trades |
| ---- | -------- | ------ | ------ |
| 1    | 10068.39 | 73.33% | 15     |
| 2    | 9741.51  | 50.00% | 18     |
| 3    | 9909.84  | 50.00% | 16     |
| 4    | 10184.61 | 70.00% | 20     |

**4/4 folds cruzam 45%.** Fold_std_hit = 10.90 pp — homogeneidade intermediária (SOL 11.04,
BTC 9.65).

### MC (500, seed=42)

p5=9191.59 | p50=9895.14 | p95=10519.01

## Quadro cross-asset Bollinger 20/2 completo

| piloto  | asset | fe       | hit    | trades | mdd   | rank | score |
| ------- | ----- | -------- | ------ | ------ | ----- | ---- | ----- |
| I.1     | SOL   | 10189.15 | 65.85% | 82     | 6.93% | 2    | 7.19  |
| I.2     | BTC   | 10033.00 | 65.85% | 82     | 2.80% | 1    | 7.70  |
| **I.3** | **ETH** | **10057.17** | **63.41%** | **82** | **5.17%** | **3** | **7.12** |

**Trio completo: todos cruzam 45%, todos têm exatamente 82 trades, top-3 do ranking N=15.**
