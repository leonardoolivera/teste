# BACKTEST.md — S.1 RSI 14/30/70 BTC 1h 2024 + atr_regime:50

## Dataset

`btcusdt_1h_20240705_20241231_binance_spot` — 4320 barras 1h.

## Métricas

### Baseline (custos H.1 + atr_regime:50 filter)

| Métrica        |    Valor |
| -------------- | -------: |
| final_equity   | 10097.54 |
| total_pnl      |   +97.54 |
| trade_count    |       55 |
| hit_rate       |   65.45% |
| max_drawdown   |     n/a  |

### Cost stress

| Cenário   | final_equity |   ratio | Δ vs baseline |
| --------- | -----------: | ------: | ------------: |
| baseline  |     10097.54 |   1.000 |             — |
| fee+10    |      9877.57 |  0.9782 |       −219.97 |
| spread+10 |      9877.57 |  0.9782 |       −219.97 |

`fee+10 ≡ spread+10 = 9877.57` (ADR-0019 **41ª confirmação**). Stress
**abaixo de 10000** — filtro não imuniza RSI contra custos.

### Monte Carlo (1000 resamples, seed=42)

- p5  = 9851.08
- p50 = 10186.12
- p95 = 10521.47

**MC p5 < 10000** — gate 3 ADR-0025 passa (0.9782 ≥ 0.95) mas
distribuição probabilística sugere cenário pessimista negativo.

## S.1 vs N.2 BTC RSI (baseline sem filtro)

| Métrica | N.2 raw | S.1 (+atr:50) | Δ |
|---------|--------:|--------------:|---:|
| trades | 64 | 55 | −14% |
| hit | 67.19% | 65.45% | −1.74pp |
| fe | 10117.76 | 10097.54 | −20 |
| MC p5 | ~9820 | 9851.08 | ~+30 |
| ratio | 0.9747 | 0.9782 | +0.0035 |

**Filtro ATR em RSI é net wash**: remove 14% trades, perde 1.74pp hit
e 20 fe, ganha marginal 0.0035 ratio. **Não generaliza cross-family.**
