# BACKTEST.md - AH.1

> Gate: **backtest**.

## Dataset

ethusdt_1h_20230705_20231231_binance_spot

## Métricas baseline

| Métrica | Valor |
|---------|------:|
| trades | 10 |
| hit_rate | 0.5000 |
| final_equity | 10042.40 |
| max_drawdown | 0.0055 |

## Stress

- spread+10bps: 10002.36 (ratio 0.9960)

## Monte Carlo

- p5: 9904.45

## Observação

2023-H2 ETH tem AMOSTRA INSUFICIENTE (10 trades). Filtro ATR:105 quase totalmente inativo em 2023 (baixa vol). Hit 50% é ruído. NÃO confirma 5/5 janelas — é estatisticamente inconclusivo.
