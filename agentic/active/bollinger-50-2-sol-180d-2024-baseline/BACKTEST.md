# BACKTEST.md — K.4 Bollinger 50/2 SOL 180d 2024

## Dataset

`solusdt_1h_20240705_20241231_binance_spot`.

## Métricas

### Baseline

| métrica      | valor    |
| ------------ | -------- |
| final_equity | 9990.02 (−0.10%, neutro) |
| hit_rate     | 61.54%   |
| total_trades | 39 (−55% vs J.1) |
| max_drawdown | 6.96%    |

### Stress

| scenario  | fe      | hit    |
| --------- | ------- | ------ |
| baseline  | 9990.02 | 61.54% |
| fee+10    | 9834.20 | 58.97% |
| slip+5    | 9975.44 | 61.54% |
| spread+10 | 9834.20 | 58.97% |

### WF (4 folds)

| fold | hit    |
| ---- | ------ |
| 1    | **75.00%** |
| 2    | 57.14% |
| 3    | **75.00%** |
| 4    | 50.00% |

### MC (500, seed=42)

p5=9542.61 | p50=10287.11 | p95=11034.46

## Leitura

Janela longa reduz trades em 55% vs baseline. Hit mantém-se >60%, mas fe fica neutro.
Janela longa perde responsividade; edge se dilui no volume baixo.
