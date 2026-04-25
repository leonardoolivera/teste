# BACKTEST.md - AB.1

## Dataset

`solusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 9913.25 |
| total_pnl | -86.75 |
| trade_count | 52 |
| hit_rate | 55.77% |
| max_drawdown | 6.35% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 9913.25 | 1.000 |
| fee+10 | 9705.63 | 0.9791 |
| spread+10 | 9705.63 | 0.9791 |

`fee+10 ≡ spread+10 = 9705.63` (ADR-0019 Série AB).

## Monte Carlo

p5 = 9610.71.

## Série AB - RSI SOL + atr thr=100 (cross-family cross-asset)
