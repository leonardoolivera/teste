# BACKTEST.md — Q.2 Bollinger ETH 1h 2024 + atr_regime

## Dataset

`ethusdt_1h_20240705_20241231_binance_spot` — 4320 barras 1h.

## Métricas

### Baseline (custos H.1 + atr_regime filter)

| Métrica        |    Valor |
| -------------- | -------: |
| final_equity   | 10119.65 |
| total_pnl      |  +119.65 |
| trade_count    |       80 |
| hit_rate       |   73.75% |
| max_drawdown   |    5.93% |

**fe > 10000** — Q.2 corrige a única fe sub-capital entre Bollinger
`canary_only`: J.3 tinha fe=9977.19; Q.2 tem 10119.65 (+142.46).

### Cost stress

| Cenário   | final_equity |   ratio | Δ vs baseline |
| --------- | -----------: | ------: | ------------: |
| baseline  |     10119.65 |   1.000 |             — |
| fee+10    |      9799.73 |  0.9684 |       −319.92 |
| spread+10 |      9799.73 |  0.9684 |       −319.92 |

`fee+10 ≡ spread+10 = 9799.73` (ADR-0019 **38ª confirmação**).

### Monte Carlo (1000 resamples, seed=42)

- p5  = 9753.11
- p50 = 10371.53
- p95 = 10909.45

## Comparação vs J.3 (baseline sem filtro) — Q.2 **DOMINA**

| Métrica        | J.3 (sem filtro) | Q.2 (+atr) | Δ |
| -------------- | ---------------: | ---------: | -: |
| hit_rate       |           71.76% |   **73.75%** | **+1.99 pp** |
| final_equity   |          9977.19 | **10119.65** | **+142.46** (cruza 10000) |
| max_drawdown   |            5.93% |      5.93% | 0.00 pp |
| trade_count    |               85 |         80 | −5 (−5.9%) |
| MC p5          |          9732.77 |    9753.11 | +20.34 |
| spread ratio   |           0.9660 |   **0.9684** | **+0.0024** |

**Leitura:** Em ETH 2024-H2, `atr_regime:14:50` filtra ~6% dos sinais
(85→80) e melhora TODAS as métricas operacionais simultaneamente. Efeito
similar a P.2 BTC mas de magnitude menor: ETH tem volatilidade intermediária
entre BTC e SOL, então filtro aciona algumas vezes mas não dominantemente.
