# BACKTEST.md - U.2

## Dataset

`ethusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10619.72 |
| total_pnl | +619.72 |
| trade_count | 38 |
| hit_rate | 73.68% |
| max_drawdown | 2.58% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10619.72 | 1.000 |
| fee+10 | 10466.63 | 0.9856 |
| spread+10 | 10466.63 | 0.9856 |

`fee+10 ≡ spread+10 = 10466.63` (ADR-0019 Série U).

## Monte Carlo

p5 = 10234.37.

## Série U - ETH refine above T.5 - MC p5 plateau
