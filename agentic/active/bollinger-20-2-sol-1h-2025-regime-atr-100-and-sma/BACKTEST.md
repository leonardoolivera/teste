# BACKTEST.md - AC.2

## Dataset

`solusdt_1h_20250705_20251231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 9638.96 |
| total_pnl | -361.04 |
| trade_count | 60 |
| hit_rate | 55.00% |
| max_drawdown | 7.76% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 9638.96 | 1.000 |
| fee+10 | 9399.92 | 0.9752 |
| spread+10 | 9399.92 | 0.9752 |

`fee+10 ≡ spread+10 = 9399.92` (ADR-0019 Série AC).

## Monte Carlo

p5 = 8930.31.

## Série AC - SOL AND OOS 2025 - AND does not help cross-window
