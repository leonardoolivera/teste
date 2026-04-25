# BACKTEST.md — P.3 Bollinger BTC 1h 2024 + composite AND

## Dataset

`btcusdt_1h_20240705_20241231_binance_spot` — 4320 barras 1h.

## Métricas

### Baseline (custos H.1 + composite AND filter)

| Métrica        |    Valor |
| -------------- | -------: |
| final_equity   | 10252.71 |
| total_pnl      |  +252.71 |
| trade_count    |       73 |
| hit_rate       |   71.23% |
| max_drawdown   |    3.63% |

### Cost stress

| Cenário   | final_equity |   ratio | Δ vs baseline |
| --------- | -----------: | ------: | ------------: |
| baseline  |     10252.71 |   1.000 |             — |
| fee+10    |      9960.50 |  0.9715 |       −292.21 |
| spread+10 |      9960.50 |  0.9715 |       −292.21 |

`fee+10 ≡ spread+10 = 9960.4985` (ADR-0019 **36ª confirmação**, primeira com
`CompositeFilter(mode="and")`).

### Monte Carlo (1000 resamples, seed=42)

- p5  = 9995.84
- p50 = 10303.78
- p95 = 10577.37

## Sweep P.1 ↔ P.2 ↔ P.3 (J.2 BTC Bollinger + diferentes filtros)

| Pilot | filtro | trades | hit | fe | MC p5 | ratio | decisão |
|-------|--------|-------:|----:|---:|------:|------:|---------|
| J.2 | nenhum | 85 | 68.24% | 10252.14 | 9921.73 | 0.9668 | canary_only |
| P.1 | sma_slope | 86 | 66.28% | 10184.11 | 10003.03 | 0.9662 | canary_only |
| **P.2** | **atr_regime** | **72** | **73.61%** | **10316.93** | 9971.33 | **0.9721** | **canary_only** |
| P.3 | AND(atr, sma) | 73 | 71.23% | 10252.71 | **9995.84** | 0.9715 | canary_only |

**Leitura:** P.3 (AND) perde para P.2 (ATR puro) em hit (−2.38 pp), fe
(−64.22) e ratio (−0.0006) mas ganha MC p5 (+24.51). Composição AND
adiciona apenas 1 trade vs P.2 — sma_slope vira restrição quase inativa
em cima de atr_regime. **P.2 domina P.3 operacionalmente; P.3 tem MC p5
marginalmente melhor mas não justifica complexidade AND.**

## Comparação com J.2

P.3 empata fe com J.2 (+0.57) mas ganha em hit (+2.99 pp), MC p5 (+74.11)
e ratio (+0.0047). Domina J.2 em todas as dimensões exceto fe marginal.
