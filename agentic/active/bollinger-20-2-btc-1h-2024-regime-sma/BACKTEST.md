# BACKTEST.md — P.1 Bollinger BTC 1h 2024 + sma_slope

## Dataset

`btcusdt_1h_20240705_20241231_binance_spot` — 4320 barras 1h.

## Métricas

### Baseline (custos H.1 + sma_slope filter)

| Métrica        |    Valor |
| -------------- | -------: |
| final_equity   | 10184.11 |
| total_pnl      |  +184.11 |
| trade_count    |       86 |
| hit_rate       |   66.28% |
| max_drawdown   |    3.63% |

### Cost stress

| Cenário   | final_equity |   ratio | Δ vs baseline |
| --------- | -----------: | ------: | ------------: |
| baseline  |     10184.11 |   1.000 |             — |
| fee+10    |      9840.09 |  0.9662 |       −344.02 |
| spread+10 |      9840.09 |  0.9662 |       −344.02 |

`fee+10 ≡ spread+10 = 9840.0884` (ADR-0019 34ª confirmação, primeira sobre
Bollinger + regime filter bit-a-bit).

### Monte Carlo (1000 resamples, seed=42)

- p5  = 10003.03
- p50 = 10335.16
- p95 = 10630.54

## Comparação vs J.2 (baseline sem filtro)

| Métrica        | J.2 (sem filtro) | P.1 (+sma) | Δ |
| -------------- | ---------------: | ---------: | -: |
| hit_rate       |           68.24% |     66.28% | **−1.96 pp** |
| final_equity   |         10252.14 |   10184.11 | −68.03 |
| max_drawdown   |            3.62% |      3.63% | +0.01 pp |
| trade_count    |               85 |         86 | +1 |
| MC p5          |          9921.73 |   10003.03 | **+81.30** |
| spread ratio   |           0.9668 |     0.9662 | −0.0006 |

**Leitura:** `sma_slope` filtro não reduz trade count (85→86) — regime
trending já é raro em mean-reversion natural do dataset. Filtro apenas
reordena timing marginalmente, perde hit mas ganha MC p5. **Custo/benefício
marginal; não melhora materialmente o handoff.**
