# BACKTEST.md - T.6 Bollinger ETH 1h 2024 + atr_regime:130

## Dataset

`ethusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10299.18 |
| total_pnl | +299.18 |
| trade_count | 14 |
| hit_rate | 85.71% |
| max_drawdown | 2.31% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10299.18 | 1.000 |
| fee+10 | 10242.64 | 0.9945 |
| spread+10 | 10242.64 | 0.9945 |

`fee+10 ≡ spread+10 = 10242.64` (ADR-0019 Série T).

## Monte Carlo

p5 = 9953.93.

## Curva ETH+atr_regime

T.6: above ETH q75 (112.8) - over-filter edge: 14tr, trivial ratio 0.9945.
