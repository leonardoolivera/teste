# BACKTEST.md - V.2

## Dataset

`btcusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10218.58 |
| total_pnl | +218.58 |
| trade_count | 25 |
| hit_rate | 64.00% |
| max_drawdown | 2.22% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10218.58 | 1.000 |
| fee+10 | 10118.24 | 0.9902 |
| spread+10 | 10118.24 | 0.9902 |

`fee+10 ≡ spread+10 = 10118.24` (ADR-0019 Série V).

## Monte Carlo

p5 = 10005.76.

## Série V - BTC refine above T.2 - over-filter edge
