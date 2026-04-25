# BACKTEST.md - AB.2

## Dataset

`ethusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10458.17 |
| total_pnl | +458.17 |
| trade_count | 40 |
| hit_rate | 67.50% |
| max_drawdown | 2.44% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10458.17 | 1.000 |
| fee+10 | 10297.41 | 0.9846 |
| spread+10 | 10297.41 | 0.9846 |

`fee+10 ≡ spread+10 = 10297.41` (ADR-0019 Série AB).

## Monte Carlo

p5 = 10144.65.

## Série AB - RSI ETH + atr thr=90 - BEST RSI of protocol
