# BACKTEST.md - Z.1

## Dataset

`solusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10743.71 |
| total_pnl | +743.71 |
| trade_count | 81 |
| hit_rate | 69.14% |
| max_drawdown | 3.43% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10743.71 | 1.000 |
| fee+10 | 10418.55 | 0.9697 |
| spread+10 | 10418.55 | 0.9697 |

`fee+10 ≡ spread+10 = 10418.55` (ADR-0019 Série Z).

## Monte Carlo

p5 = 10068.97.

## Série Z - SOL curve fill-in: between Q.1(50) and R.1(100)
