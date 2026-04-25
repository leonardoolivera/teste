# BACKTEST.md - Y.2

## Dataset

`solusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 9580.01 |
| total_pnl | -419.99 |
| trade_count | 93 |
| hit_rate | 45.16% |
| max_drawdown | 6.48% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 9580.01 | 1.000 |
| fee+10 | 9209.22 | 0.9613 |
| spread+10 | 9209.22 | 0.9613 |

`fee+10 ≡ spread+10 = 9209.22` (ADR-0019 Série Y).

## Monte Carlo

p5 = 8761.82.

## Série Y - Donchian SOL + atr - cross-strategy filter test
