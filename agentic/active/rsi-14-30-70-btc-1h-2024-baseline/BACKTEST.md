# BACKTEST.md — N.2 RSI 14/30/70 BTC 1h 2024

## Dataset

`btcusdt_1h_20240705_20241231_binance_spot` — 4320 barras 1h.

## Métricas

### Baseline (custos H.1)

| Métrica        |    Valor |
| -------------- | -------: |
| final_equity   | 10117.99 |
| total_pnl      |  +117.99 |
| trade_count    |       64 |
| hit_rate       |   67.19% |
| max_drawdown   |    3.46% |

## Cost stress

| Cenário   | final_equity | Δ vs baseline |
| --------- | -----------: | ------------: |
| baseline  |     10117.99 |             — |
| fee+10    |      9862.02 |       −255.97 |
| slip+10   |     10066.71 |        −51.28 |
| spread+10 |      9862.02 |       −255.97 |

`fee+10 == spread+10` exato (ADR-0019, 30ª confirmação).

## Monte Carlo

- p5  = 9878.93
- p50 = 10217.01
- p95 = 10492.00

## Relação com J.2 (Bollinger BTC 1h 2024)

N.2 é o **melhor RSI do trio** em hit e baseline fe positivo. BTC é o asset onde
RSI mais se aproxima de Bollinger. Comparação detalhada em AUDIT.md.
