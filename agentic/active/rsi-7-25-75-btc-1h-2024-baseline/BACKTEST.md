# BACKTEST.md — O.1 RSI 7/25/75 BTC 1h 2024

## Dataset

`btcusdt_1h_20240705_20241231_binance_spot` — 4320 barras 1h.

## Métricas

### Baseline (custos H.1)

| Métrica        |    Valor |
| -------------- | -------: |
| final_equity   | 10128.01 |
| total_pnl      |  +128.01 |
| trade_count    |      147 |
| hit_rate       |   59.86% |
| max_drawdown   |    4.46% |

### Cost stress

| Cenário   | final_equity | Δ vs baseline |
| --------- | -----------: | ------------: |
| baseline  |     10128.01 |             — |
| fee+10    |      9538.35 |       −589.66 |
| slip+10   |     10009.93 |       −118.08 |
| spread+10 |      9538.35 |       −589.66 |

`fee+10 ≡ spread+10 = 9538.35` (ADR-0019 32ª confirmação).

**Sensibilidade a custos é 2.3× maior que N.2 em termos absolutos** (−590 vs
−256 USDT) — reflexo dos 147 trades (vs 64 em N.2, +130%). Custo marginal por
trade é idêntico; o que muda é o número de trades.

### Monte Carlo

- p5  = 9931.16
- p50 = 10297.43
- p95 = 10657.56

## Comparação O.1 ↔ N.2 ↔ J.2 (BTC 1h 2024-H2)

| Dimensão | J.2 Bollinger | N.2 RSI 14/30/70 | O.1 RSI 7/25/75 |
| -------- | ------------: | ---------------: | --------------: |
| trades   |            85 |               64 |             147 |
| hit      |        68.24% |           67.19% |          59.86% |
| fe       |      10252.14 |         10117.99 |        10128.01 |
| mdd      |         3.62% |            3.46% |           4.46% |
| spread ratio | 0.9751  |           0.9747 |      **0.9418** |
| MC p5    |      10046.92 |          9878.93 |         9931.16 |

O.1 tem **MC p5 > N.2** (+52 USDT) — distribuição superior por Monte Carlo, mas
falha Critério 3 (frequência quebra custo). Edge médio existe mas é economicamente
frágil — padrão típico de overfitting a regime favorável.
