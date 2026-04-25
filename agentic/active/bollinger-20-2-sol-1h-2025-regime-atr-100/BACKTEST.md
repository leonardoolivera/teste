# BACKTEST.md - W.1

## Dataset

`solusdt_1h_20250705_20251231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 9475.95 |
| total_pnl | -524.05 |
| trade_count | 58 |
| hit_rate | 53.45% |
| max_drawdown | 8.21% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 9475.95 | 1.000 |
| fee+10 | 9245.23 | 0.9757 |
| spread+10 | 9245.23 | 0.9757 |

`fee+10 ≡ spread+10 = 9245.23` (ADR-0019 Série W).

## Monte Carlo

p5 = 8772.55.

## Série W - OOS 2025-H2 test of R.1 sweet spot
