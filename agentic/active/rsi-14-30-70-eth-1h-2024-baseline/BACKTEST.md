# BACKTEST.md — N.3 RSI 14/30/70 ETH 1h 2024

## Dataset

`ethusdt_1h_20240705_20241231_binance_spot` — 4320 barras 1h.

## Métricas

### Baseline (custos H.1)

| Métrica        |    Valor |
| -------------- | -------: |
| final_equity   |  9900.11 |
| total_pnl      |   −99.89 |
| trade_count    |       75 |
| hit_rate       |   69.33% |
| max_drawdown   |    5.71% |

**Hit rate 69.33% é o maior do trio N** — RSI tem melhor calibração de sinal em
ETH 2024-H2, mesmo com fe ligeiramente negativo (custos comem PnL).

## Cost stress

| Cenário   | final_equity | Δ vs baseline |
| --------- | -----------: | ------------: |
| baseline  |      9900.11 |             — |
| fee+10    |      9600.61 |       −299.50 |
| slip+10   |      9840.15 |        −59.96 |
| spread+10 |      9600.61 |       −299.50 |

`fee+10 == spread+10` exato (ADR-0019, 31ª confirmação do protocolo).

## Monte Carlo

- p5  = 9665.78
- p50 = 10128.86
- p95 = 10620.69

## Comparação com trio J Bollinger

| Asset | J Bollinger (hit/fe) | N RSI (hit/fe) |
| ----- | -------------------: | -------------: |
| SOL   |     67.82% / 10684   | 58.73% /  9850 |
| BTC   |     68.24% / 10252   | 67.19% / 10118 |
| ETH   |     ~66% / ~10300 (J.3) | 69.33% /  9900 |

ETH é asset onde **hit_rate RSI > Bollinger** (+3 pp aprox), mas fe RSI < fe
Bollinger — custos comem o edge extra de hit.
