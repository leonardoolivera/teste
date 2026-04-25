# BACKTEST.md - AA.1

## Dataset

`ethusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10265.68 |
| total_pnl | +265.68 |
| trade_count | 40 |
| hit_rate | 62.50% |
| max_drawdown | 2.40% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10265.68 | 1.000 |
| fee+10 | 10105.31 | 0.9844 |
| spread+10 | 10105.31 | 0.9844 |

`fee+10 ≡ spread+10 = 10105.31` (ADR-0019 Série AA).

## Monte Carlo

p5 = 10027.03.

## Série AA - Bollinger window=10 at U.2 sweet spot
