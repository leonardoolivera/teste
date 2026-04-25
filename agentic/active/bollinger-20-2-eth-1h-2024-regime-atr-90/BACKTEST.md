# BACKTEST.md - T.5 Bollinger ETH 1h 2024 + atr_regime:90

## Dataset

`ethusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10645.47 |
| total_pnl | +645.47 |
| trade_count | 48 |
| hit_rate | 75.00% |
| max_drawdown | 4.10% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10645.47 | 1.000 |
| fee+10 | 10452.38 | 0.9819 |
| spread+10 | 10452.38 | 0.9819 |

`fee+10 ≡ spread+10 = 10452.38` (ADR-0019 Série T).

## Monte Carlo

p5 = 9999.42.

## Curva ETH+atr_regime

T.5: near ETH median (88.7) - SWEET SPOT candidate: fe 10645, hit 75%, ratio 0.9819.
