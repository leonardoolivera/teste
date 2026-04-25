# BACKTEST.md — L.2 Bollinger 20/2 BTC 15m 2024

## Dataset

`btcusdt_15m_20240705_20241231_binance_spot` — 17280 barras 15m, sha256=`8ccce65c`.

## Métricas

### Baseline

| métrica      | valor    |
| ------------ | -------- |
| final_equity | 9696.67  |
| hit_rate     | 60.00%   |
| total_trades | 330      |
| max_drawdown | 5.11%    |

**Fe baseline < capital inicial (−3.03%)** — edge econômico já negativo em BTC 15m
antes mesmo do stress de custos.

### Stress

| scenario  | fe      | hit    | Δ fe    |
| --------- | ------- | ------ | ------- |
| baseline  | 9696.67 | 60.00% | —       |
| fee+10    | 8376.61 | 42.73% | **−13.61%** |
| slip+5    | 9564.53 | 58.79% | −1.36%  |
| spread+10 | 8376.61 | 42.73% | **−13.61%** |

### WF (4 folds)

| fold | hit    |
| ---- | ------ |
| 1    | 59.70% |
| 2    | 60.87% |
| 3    | 58.62% |
| 4    | 66.18% |

**4/4 folds cruzam 45%.**

### MC (500, seed=42)

p5=9603.57 | p50=10035.76 | p95=10459.55

## Comparação L.2 15m vs J.2 1h (BTC, mesma janela)

| métrica | L.2 (15m) | J.2 (1h) | Δ |
|---------|-----------|----------|---|
| hit | 60.00% | 68.24% | −8.24 pp |
| fe | 9696.67 | 10252.14 | −5.42% |
| trades | 330 | ~85 | +288% |
| mdd | 5.11% | 3.62% | +1.49 pp |
| spread+10/baseline | **0.864** | ~0.967 | gate violado |
