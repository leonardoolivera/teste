# BACKTEST.md - W.3

## Dataset

`ethusdt_1h_20250705_20251231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10077.63 |
| total_pnl | +77.63 |
| trade_count | 42 |
| hit_rate | 57.14% |
| max_drawdown | 2.53% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10077.63 | 1.000 |
| fee+10 | 9909.65 | 0.9833 |
| spread+10 | 9909.65 | 0.9833 |

`fee+10 ≡ spread+10 = 9909.65` (ADR-0019 Série W).

## Monte Carlo

p5 = 9520.61.

## Série W - OOS 2025-H2 test of U.2 sweet spot
