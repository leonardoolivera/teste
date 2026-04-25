# BACKTEST.md - T.4 Bollinger ETH 1h 2024 + atr_regime:40

## Dataset

`ethusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10031.13 |
| total_pnl | +31.13 |
| trade_count | 82 |
| hit_rate | 71.95% |
| max_drawdown | 5.93% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10031.13 | 1.000 |
| fee+10 | 9703.40 | 0.9673 |
| spread+10 | 9703.40 | 0.9673 |

`fee+10 ≡ spread+10 = 9703.40` (ADR-0019 Série T).

## Monte Carlo

p5 = 9667.34.

## Curva ETH+atr_regime

T.4: below ETH q15 (61.3) - near-baseline activation.
