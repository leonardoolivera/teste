# BACKTEST.md - V.1

## Dataset

`btcusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10398.26 |
| total_pnl | +398.26 |
| trade_count | 67 |
| hit_rate | 73.13% |
| max_drawdown | 3.62% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10398.26 | 1.000 |
| fee+10 | 10129.74 | 0.9742 |
| spread+10 | 10129.74 | 0.9742 |

`fee+10 ≡ spread+10 = 10129.74` (ADR-0019 Série V).

## Monte Carlo

p5 = 10073.02.

## Série V - BTC refine between P.2(50) and T.2(70)
