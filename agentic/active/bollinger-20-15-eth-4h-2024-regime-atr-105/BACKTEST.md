# BACKTEST.md - AH.4

> Gate: **backtest**.

## Dataset

ethusdt_4h_20240705_20241231_binance_spot

## Métricas baseline

| Métrica | Valor |
|---------|------:|
| trades | 24 |
| hit_rate | 0.5833 |
| final_equity | 9478.61 |
| max_drawdown | 0.0738 |

## Stress

- spread+10bps: 9383.75 (ratio 0.9900)

## Monte Carlo

- p5: 9301.53

## Observação

ETH 4h FALHA: fe 9478 (-5.2% capital). Edge não transfere cross-timeframe. Config 20/1.5+atr:105 é 1h-específica em ETH.
