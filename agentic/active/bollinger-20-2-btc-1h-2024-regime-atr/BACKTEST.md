# BACKTEST.md — P.2 Bollinger BTC 1h 2024 + atr_regime

## Dataset

`btcusdt_1h_20240705_20241231_binance_spot` — 4320 barras 1h.

## Métricas

### Baseline (custos H.1 + atr_regime filter)

| Métrica        |    Valor |
| -------------- | -------: |
| final_equity   | 10316.93 |
| total_pnl      |  +316.93 |
| trade_count    |       72 |
| hit_rate       |   73.61% |
| max_drawdown   |    3.62% |

### Cost stress

| Cenário   | final_equity |   ratio | Δ vs baseline |
| --------- | -----------: | ------: | ------------: |
| baseline  |     10316.93 |   1.000 |             — |
| fee+10    |     10028.59 |  0.9721 |       −288.34 |
| spread+10 |     10028.59 |  0.9721 |       −288.34 |

`fee+10 ≡ spread+10 = 10028.5915` (ADR-0019 **35ª confirmação**, **primeira vez
que cenário fee+10 e spread+10 ficam > 10000** — filtro ATR preserva edge sob
stress).

### Monte Carlo (1000 resamples, seed=42)

- p5  = 9971.33
- p50 = 10371.19
- p95 = 10675.94

## Comparação vs J.2 (baseline sem filtro) — P.2 **DOMINA**

| Métrica        | J.2 (sem filtro) | P.2 (+atr) | Δ |
| -------------- | ---------------: | ---------: | -: |
| hit_rate       |           68.24% |   **73.61%** | **+5.37 pp** |
| final_equity   |         10252.14 | **10316.93** | **+64.79** |
| max_drawdown   |            3.62% |      3.62% | 0.00 pp |
| trade_count    |               85 |        72 | −13 (−15.3%) |
| MC p5          |          9921.73 |    9971.33 | +49.60 |
| spread ratio   |           0.9668 | **0.9721** | **+0.0053** |

**Leitura:** `atr_regime` filtra sinais em baixa vol (onde mean-reversion é
fraco) e preserva os bons setups. **Trade count cai 15%**, **hit sobe +5.37 pp**,
**fe sobe +64.79**, **ratio sobe +0.0053** — ganho em TODOS os eixos
operacionais simultaneamente. Primeiro piloto a dominar J.2.
