# BACKTEST.md — Q.1 Bollinger SOL 1h 2024 + atr_regime

## Dataset

`solusdt_1h_20240705_20241231_binance_spot` — 4320 barras 1h.

## Métricas

### Baseline (custos H.1 + atr_regime filter)

| Métrica        |    Valor |
| -------------- | -------: |
| final_equity   | 10716.73 |
| total_pnl      |  +716.73 |
| trade_count    |       87 |
| hit_rate       |   67.82% |
| max_drawdown   |    3.43% |

### Cost stress

| Cenário   | final_equity |   ratio | Δ vs baseline |
| --------- | -----------: | ------: | ------------: |
| baseline  |     10716.73 |   1.000 |             — |
| fee+10    |     10367.65 |  0.9674 |       −349.08 |
| spread+10 |     10367.65 |  0.9674 |       −349.08 |

`fee+10 ≡ spread+10 = 10367.65` (ADR-0019 **37ª confirmação**, **2ª vez que
cenário stress termina > 10000 USDT** — depois de P.2 — primeira em SOL).

### Monte Carlo (1000 resamples, seed=42)

- p5  = 10064.16
- p50 = 10652.85
- p95 = 11257.29

## Comparação vs J.1 (baseline sem filtro)

| Métrica        | J.1 (sem filtro) | Q.1 (+atr) | Δ |
| -------------- | ---------------: | ---------: | -: |
| hit_rate       |           67.82% |     67.82% | **0.00 pp** |
| final_equity   |         10684.24 |   10716.73 | **+32.49** |
| max_drawdown   |            3.43% |      3.43% | 0.00 pp |
| trade_count    |               87 |         87 | **0** |
| MC p5          |         10046.92 |   10064.16 | +17.24 |
| spread ratio   |           0.9673 |     0.9674 | +0.0001 |

**Leitura:** Filtro `atr_regime:14:50` **fica quase totalmente inativo em SOL
2024-H2** — volatilidade do SOL está acima do threshold 50 bps quase continuamente
no semestre. **Apenas 1 sinal de 87 foi suprimido** (entrada 2024-09-15 11:00
reentrou 2024-09-15 17:00 após ATR cruzar threshold). Trade count idêntico (87),
hit idêntico (67.82%). Ganho material é +32.49 em fe e +17.24 em MC p5 via
timing marginal do 1 trade realocado. **Filtro ATR tem valor zero como
filtro em SOL**; atua como micro-delay quando ATR cai brevemente.
