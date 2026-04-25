# BACKTEST.md - AC.3

## Dataset

`ethusdt_1h_20250705_20251231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 9941.28 |
| total_pnl | -58.72 |
| trade_count | 21 |
| hit_rate | 61.90% |
| max_drawdown | 3.55% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 9941.28 | 1.000 |
| fee+10 | 9857.49 | 0.9916 |
| spread+10 | 9857.49 | 0.9916 |

`fee+10 ≡ spread+10 = 9857.49` (ADR-0019 Série AC).

## Monte Carlo

p5 = 9547.52.

## Série AC - ETH thr=130 OOS 2025 - T.6 degrades
