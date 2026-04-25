# BACKTEST.md - X.1

## Dataset

`btcusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10321.55 |
| total_pnl | +321.55 |
| trade_count | 67 |
| hit_rate | 71.64% |
| max_drawdown | 3.63% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10321.55 | 1.000 |
| fee+10 | 10053.18 | 0.9740 |
| spread+10 | 10053.18 | 0.9740 |

`fee+10 ≡ spread+10 = 10053.18` (ADR-0019 Série X).

## Monte Carlo

p5 = 9996.73.

## Série X - BTC AND filter at V.1 sweet spot
