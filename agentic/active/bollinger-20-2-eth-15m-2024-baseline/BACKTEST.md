# BACKTEST.md — L.3 Bollinger 20/2 ETH 15m 2024

## Dataset

`ethusdt_15m_20240705_20241231_binance_spot` — 17280 barras 15m, sha256=`324086d8`.

## Métricas

### Baseline

| métrica      | valor    |
| ------------ | -------- |
| final_equity | 9769.61  |
| hit_rate     | 61.76%   |
| total_trades | 353      |
| max_drawdown | 9.32%    |

**Fe baseline < capital inicial (−2.30%)** — edge econômico negativo (como BTC 15m).

### Stress

| scenario  | fe      | hit    | Δ fe    |
| --------- | ------- | ------ | ------- |
| baseline  | 9769.61 | 61.76% | —       |
| fee+10    | 8357.51 | 48.16% | **−14.45%** |
| slip+5    | 9628.25 | 59.77% | −1.45%  |
| spread+10 | 8357.51 | 48.16% | **−14.45%** |

**Pior sensibilidade do trio L (−14.45% vs −12.90% SOL e −13.61% BTC).**

### WF (4 folds)

| fold | hit    |
| ---- | ------ |
| 1    | 52.24% |
| 2    | 66.67% |
| 3    | 64.86% |
| 4    | 65.28% |

**4/4 folds cruzam 45%.**

### MC (500, seed=42)

p5=9472.05 | p50=10162.12 | p95=10759.86

## Quadro consolidado trio L (15m, 2024-H2)

| asset | hit baseline | fe | mdd | spread+10/base | status |
|-------|--------------|-----|-----|----------------|--------|
| SOL (L.1) | 63.10% | 10433.99 | 5.53% | 0.871 | fail |
| BTC (L.2) | 60.00% | 9696.67 | 5.11% | 0.864 | fail |
| ETH (L.3) | 61.76% | 9769.61 | 9.32% | 0.855 | fail |

**3/3 fail. Propriedade do timeframe confirmada.**
