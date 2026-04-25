# BACKTEST.md - X.3

## Dataset

`solusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10707.20 |
| total_pnl | +707.20 |
| trade_count | 64 |
| hit_rate | 68.75% |
| max_drawdown | 3.49% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10707.20 | 1.000 |
| fee+10 | 10450.05 | 0.9760 |
| spread+10 | 10450.05 | 0.9760 |

`fee+10 ≡ spread+10 = 10450.05` (ADR-0019 Série X).

## Monte Carlo

p5 = 10327.29.

## Série X - SOL AND filter at R.1 - best MC p5 of protocol
