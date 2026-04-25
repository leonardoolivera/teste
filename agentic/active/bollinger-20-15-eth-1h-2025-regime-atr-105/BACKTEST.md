# BACKTEST.md - AC.1

## Dataset

`ethusdt_1h_20250705_20251231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10465.68 |
| total_pnl | +465.68 |
| trade_count | 53 |
| hit_rate | 64.15% |
| max_drawdown | 2.50% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10465.68 | 1.000 |
| fee+10 | 10252.97 | 0.9797 |
| spread+10 | 10252.97 | 0.9797 |

`fee+10 ≡ spread+10 = 10252.97` (ADR-0019 Série AC).

## Monte Carlo

p5 = 9728.18.

## Série AC - ETH 20/1.5 OOS 2025 - PRESERVES edge
