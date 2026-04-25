# BACKTEST.md - AA.2

## Dataset

`ethusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10224.43 |
| total_pnl | +224.43 |
| trade_count | 23 |
| hit_rate | 52.17% |
| max_drawdown | 3.64% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10224.43 | 1.000 |
| fee+10 | 10132.07 | 0.9910 |
| spread+10 | 10132.07 | 0.9910 |

`fee+10 ≡ spread+10 = 10132.07` (ADR-0019 Série AA).

## Monte Carlo

p5 = 9809.84.

## Série AA - Bollinger window=30 at U.2 sweet spot
