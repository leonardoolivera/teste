# BACKTEST.md — K.3 Bollinger 10/2 SOL 180d 2024

## Dataset

`solusdt_1h_20240705_20241231_binance_spot`.

## Métricas

### Baseline

| métrica      | valor    |
| ------------ | -------- |
| final_equity | 10671.75 |
| hit_rate     | 59.54%   |
| total_trades | 131      |
| max_drawdown | **2.26%** (menor do protocolo) |

### Stress

| scenario  | fe       | hit    |
| --------- | -------- | ------ |
| baseline  | 10671.75 | 59.54% |
| fee+10    | 10146.94 | 53.44% |
| slip+5    | 10620.65 | 59.54% |
| spread+10 | 10146.94 | 53.44% |

### WF (4 folds)

| fold | hit    |
| ---- | ------ |
| 1    | 64.52% |
| 2    | 56.00% |
| 3    | 68.42% |
| 4    | 56.67% |

### MC (500, seed=42)

p5=9911.00 | p50=10521.35 | p95=11131.70

## Leitura

Janela curta = alta reatividade, mais trades (131), maior sensibilidade a custos
(spread+10 ratio 0.951 no limite), **mas menor mdd do protocolo** (2.26%).
