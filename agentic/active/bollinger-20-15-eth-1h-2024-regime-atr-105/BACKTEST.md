# BACKTEST.md - AA.3

## Dataset

`ethusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10540.91 |
| total_pnl | +540.91 |
| trade_count | 38 |
| hit_rate | 63.16% |
| max_drawdown | 2.83% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10540.91 | 1.000 |
| fee+10 | 10387.98 | 0.9855 |
| spread+10 | 10387.98 | 0.9855 |

`fee+10 ≡ spread+10 = 10387.98` (ADR-0019 Série AA).

## Monte Carlo

p5 = 10160.70.

## Série AA - Bollinger num_std=1.5 at U.2 sweet spot
