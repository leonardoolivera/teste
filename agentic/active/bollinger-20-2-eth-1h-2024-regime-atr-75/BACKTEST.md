# BACKTEST.md - U.1

## Dataset

`ethusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10420.95 |
| total_pnl | +420.95 |
| trade_count | 59 |
| hit_rate | 74.58% |
| max_drawdown | 4.80% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10420.95 | 1.000 |
| fee+10 | 10184.35 | 0.9773 |
| spread+10 | 10184.35 | 0.9773 |

`fee+10 ≡ spread+10 = 10184.35` (ADR-0019 Série U).

## Monte Carlo

p5 = 10051.12.

## Série U - ETH refine below T.5 peak
