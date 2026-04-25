# BACKTEST.md - AG.1

> Gate: **backtest**.

## Dataset

ethusdt_1h_20240105_20240704_binance_spot (4368 barras, 2024-H1).

## Métricas baseline

| Métrica | Valor |
|---------|------:|
| trades | 40 |
| hit_rate | 0.7750 |
| final_equity | 10654.54 |
| max_drawdown | 0.0259 |

## Stress

- spread+10bps: 10491.29 (ratio 0.9847)

## Monte Carlo

- p5: 10361.25

## ETH 20/1.5+atr:105 em 4 janelas consecutivas

| Janela | hit | fe | ratio |
|--------|----:|---:|------:|
| 2024-H1 (AG.1) | 77.50% | 10654 | 0.9847 |
| 2024-H2 (AA.3) | 63.16% | 10540 | 0.9855 |
| 2025-H1 (AF.2) | 62.90% | 10376 | 0.9761 |
| 2025-H2 (AC.1) | 64.15% | 10465 | 0.9797 |

**4/4 preservam edge.** Hit 63-77% (variação 14pp). fe sempre > 10300. Ratio sempre > 0.976.

