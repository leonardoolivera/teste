# BACKTEST.md - Z.2

## Dataset

`solusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10498.38 |
| total_pnl | +498.38 |
| trade_count | 43 |
| hit_rate | 65.12% |
| max_drawdown | 2.89% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10498.38 | 1.000 |
| fee+10 | 10325.56 | 0.9835 |
| spread+10 | 10325.56 | 0.9835 |

`fee+10 ≡ spread+10 = 10325.56` (ADR-0019 Série Z).

## Monte Carlo

p5 = 10085.90.

## Série Z - SOL curve fill-in: between R.1(100) and R.2(150)
