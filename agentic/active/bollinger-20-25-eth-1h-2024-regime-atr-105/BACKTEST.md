# BACKTEST.md - AA.4

## Dataset

`ethusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10341.56 |
| total_pnl | +341.56 |
| trade_count | 20 |
| hit_rate | 65.00% |
| max_drawdown | 2.64% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10341.56 | 1.000 |
| fee+10 | 10260.96 | 0.9922 |
| spread+10 | 10260.96 | 0.9922 |

`fee+10 ≡ spread+10 = 10260.96` (ADR-0019 Série AA).

## Monte Carlo

p5 = 9987.25.

## Série AA - Bollinger num_std=2.5 at U.2 sweet spot
