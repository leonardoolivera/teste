# BACKTEST.md — K.2 Bollinger 20/2.5 SOL 180d 2024

## Dataset

`solusdt_1h_20240705_20241231_binance_spot`.

## Métricas

### Baseline

| métrica      | valor    |
| ------------ | -------- |
| final_equity | 10191.16 |
| hit_rate     | 62.00%   |
| total_trades | 50 (−43% vs J.1) |
| max_drawdown | 3.42%    |

### Stress

| scenario  | fe      | hit    |
| --------- | ------- | ------ |
| baseline  | 10191.16 | 62.00% |
| fee+10    | 9990.99  | 60.00% |
| slip+5    | 10175.10 | 62.00% |
| spread+10 | 9990.99  | 60.00% |

### WF (4 folds)

| fold | hit    |
| ---- | ------ |
| 1    | 66.67% |
| 2    | 44.44% |
| 3    | **83.33%** |
| 4    | 63.64% |

### MC (500, seed=42)

p5=9688.08 | p50=10169.51 | p95=10638.56

## Comparação K.2 (2.5) vs J.1 (2.0)

Menos trades (−43%), hit marginalmente menor, fe menor. Banda mais larga é mais seletiva
mas perde oportunidades — trade-off oposto a K.1.
