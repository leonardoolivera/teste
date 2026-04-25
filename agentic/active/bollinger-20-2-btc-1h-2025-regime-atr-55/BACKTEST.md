# BACKTEST.md - W.2

## Dataset

`btcusdt_1h_20250705_20251231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10067.14 |
| total_pnl | +67.14 |
| trade_count | 42 |
| hit_rate | 52.38% |
| max_drawdown | 1.82% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10067.14 | 1.000 |
| fee+10 | 9899.18 | 0.9833 |
| spread+10 | 9899.18 | 0.9833 |

`fee+10 ≡ spread+10 = 9899.18` (ADR-0019 Série W).

## Monte Carlo

p5 = 9715.77.

## Série W - OOS 2025-H2 test of V.1 sweet spot
