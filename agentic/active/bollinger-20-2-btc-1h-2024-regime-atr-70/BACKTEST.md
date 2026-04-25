# BACKTEST.md - T.2 Bollinger BTC 1h 2024 + atr_regime:70

## Dataset

`btcusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10272.86 |
| total_pnl | +272.86 |
| trade_count | 44 |
| hit_rate | 68.18% |
| max_drawdown | 3.58% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10272.86 | 1.000 |
| fee+10 | 10096.49 | 0.9828 |
| spread+10 | 10096.49 | 0.9828 |

`fee+10 ≡ spread+10 = 10096.49` (ADR-0019 Série T).

## Monte Carlo

p5 = 10081.02.

## Curva BTC+atr_regime

T.2: near BTC median ATR (70.7) - mid-curve; lower trades but fe preserved.
