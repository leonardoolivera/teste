# BACKTEST.md - X.2

## Dataset

`ethusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10564.65 |
| total_pnl | +564.65 |
| trade_count | 37 |
| hit_rate | 72.97% |
| max_drawdown | 2.59% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10564.65 | 1.000 |
| fee+10 | 10415.68 | 0.9859 |
| spread+10 | 10415.68 | 0.9859 |

`fee+10 ≡ spread+10 = 10415.68` (ADR-0019 Série X).

## Monte Carlo

p5 = 10111.50.

## Série X - ETH AND filter at U.2 sweet spot
