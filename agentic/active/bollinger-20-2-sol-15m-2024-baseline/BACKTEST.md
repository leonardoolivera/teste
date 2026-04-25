# BACKTEST.md — L.1 Bollinger 20/2 SOL 15m 2024

## Dataset

`solusdt_15m_20240705_20241231_binance_spot` — 17280 barras 15m, sha256=`589d8165`.

## Métricas

### Baseline

| métrica      | valor    |
| ------------ | -------- |
| final_equity | 10433.99 |
| hit_rate     | 63.10%   |
| total_trades | 336 (3.9× J.1) |
| max_drawdown | 5.53%    |

### Stress

| scenario  | fe      | hit    | Δ fe    |
| --------- | ------- | ------ | ------- |
| baseline  | 10433.99 | 63.10% | —       |
| fee+10    | 9088.47  | 52.68% | **−12.89%** |
| slip+5    | 10307.07 | 63.10% | −1.22%  |
| spread+10 | 9088.47  | 52.68% | **−12.89%** |

**Sensibilidade a fee/spread é 4× maior que em 1h** (−12.89% vs −3.27% em J.1).

### WF (4 folds)

| fold | hit    |
| ---- | ------ |
| 1    | 56.45% |
| 2    | 68.25% |
| 3    | 64.62% |
| 4    | 64.38% |

**4/4 folds cruzam 45%.**

### MC (500, seed=42)

p5=9563.37 | p50=10316.03 | p95=11110.66

## Comparação L.1 15m vs J.1 1h (mesmo asset, mesma janela)

| métrica | L.1 (15m) | J.1 (1h) | Δ |
|---------|-----------|----------|---|
| hit | 63.10% | 67.82% | −4.72 pp |
| fe | 10433.99 | 10684.24 | −2.35% |
| trades | 336 | 87 | **+286%** |
| mdd | 5.53% | 3.43% | +2.10 pp |
| fee+10 Δ | −12.89% | −3.27% | **4× pior** |
| spread+10/baseline | **0.871** | 0.967 | gate violado |
