# BACKTEST.md — R.1 Bollinger SOL 1h 2024 + atr_regime:100

## Dataset

`solusdt_1h_20240705_20241231_binance_spot` — 4320 barras 1h.

## Métricas

### Baseline (custos H.1 + atr_regime:100 filter)

| Métrica        |    Valor |
| -------------- | -------: |
| final_equity   | 10803.68 |
| total_pnl      |  +803.68 |
| trade_count    |       65 |
| hit_rate       |   70.77% |
| max_drawdown   |    3.43% |

### Cost stress

| Cenário   | final_equity |   ratio | Δ vs baseline |
| --------- | -----------: | ------: | ------------: |
| baseline  |     10803.68 |   1.000 |             — |
| fee+10    |     10542.34 |  0.9758 |       −261.34 |
| spread+10 |     10542.34 |  0.9758 |       −261.34 |

`fee+10 ≡ spread+10 = 10542.34` (ADR-0019 **39ª confirmação, 3ª vez stress
> 10000; primeira > 10500**).

### Monte Carlo (1000 resamples, seed=42)

- p5  = 10212.03
- p50 = 10696.04
- p95 = 11141.93

**MC p5 > 10200** — 2º maior MC p5 do protocolo (atrás de P.3=9995? não,
MC p5 acima de 10000 aqui é maior que qualquer P.x). **Maior MC p5 dos 38+**.

## Comparação vs J.1 (SOL sem filtro) e Q.1 (SOL+atr:50 quase inativo)

| Métrica        |   J.1 |  Q.1 |  **R.1** | Δ vs J.1 |
| -------------- | ----: | ---: | -------: | -------: |
| hit_rate       | 67.82%| 67.82%| **70.77%** | **+2.95 pp** |
| final_equity   |10684.24|10716.73| **10803.68** | **+119.44** |
| max_drawdown   | 3.43% | 3.43% |    3.43% |    0.00 pp |
| trade_count    |    87 |   87 |       65 | **−22 (−25%)** |
| MC p5          |10046.92|10064.16| **10212.03** | **+165.11** |
| spread ratio   |0.9673 |0.9674| **0.9758** | **+0.0085** |

**Leitura:** Threshold calibrado 100 bps **reativa completamente o filtro**
em SOL. Filtra 25% dos sinais (87→65), sinais filtrados tinham qualidade
marginalmente inferior (hit dos preservados sobe +2.95 pp), fe sobe +119,
MC p5 sobe +165, ratio sobe +0.0085. **Calibração por asset é a chave.**

## Inventário da atividade do filtro

Com threshold 100 bps, filtro ativa em ~25% das barras onde Bollinger
geraria sinal — SOL 2024-H2 tem muitos períodos de alta-mas-não-extrema
volatilidade onde bandas estão formadas mas edge é marginal.
