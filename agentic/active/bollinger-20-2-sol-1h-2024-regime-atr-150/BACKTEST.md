# BACKTEST.md — R.2 Bollinger SOL 1h 2024 + atr_regime:150

## Dataset

`solusdt_1h_20240705_20241231_binance_spot` — 4320 barras 1h.

## Métricas

### Baseline (custos H.1 + atr_regime:150 filter)

| Métrica        |    Valor |
| -------------- | -------: |
| final_equity   | 10420.94 |
| total_pnl      |  +420.94 |
| trade_count    |       26 |
| hit_rate       |   65.38% |
| max_drawdown   |    2.92% |

### Cost stress

| Cenário   | final_equity |   ratio | Δ vs baseline |
| --------- | -----------: | ------: | ------------: |
| baseline  |     10420.94 |   1.000 |             — |
| fee+10    |     10316.21 |  0.9899 |       −104.73 |
| spread+10 |     10316.21 |  0.9899 |       −104.73 |

`fee+10 ≡ spread+10 = 10316.21` (ADR-0019 **40ª confirmação, 4ª vez stress
> 10000**). Ratio 0.9899 é o **maior do protocolo** — amostra pequena
corta exposição a custos.

### Monte Carlo (1000 resamples, seed=42)

- p5  = 10074.98
- p50 = 10291.71
- p95 = 10557.98

## Curva de utilidade SOL+atr (Q.1 50 ↔ R.1 100 ↔ R.2 150)

| Threshold | trades | hit | fe | MC p5 | ratio | decisão |
|-----------|-------:|----:|---:|------:|------:|---------|
| — (J.1) | 87 | 67.82% | 10684.24 | 10046.92 | 0.9673 | canary_only |
| 50 (Q.1) | 87 | 67.82% | 10716.73 | 10064.16 | 0.9674 | canary_only |
| **100 (R.1)** | **65** | **70.77%** | **10803.68** | **10212.03** | **0.9758** | **canary_only** |
| 150 (R.2) | 26 | 65.38% | 10420.94 | 10074.98 | **0.9899** | canary_only |

**Curva é não-monotônica ("U invertido ou plateau decrescente"):** threshold
50 inativo, 100 é sweet spot, 150 over-filtering (fe cai, amostra pequena).
R.2 é **dominado por R.1 em fe e hit**, melhor apenas em ratio e mdd
(trivialmente, via menor exposição).
