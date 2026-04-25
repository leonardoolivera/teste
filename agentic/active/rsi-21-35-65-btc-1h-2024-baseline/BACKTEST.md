# BACKTEST.md — O.2 RSI 21/35/65 BTC 1h 2024

## Dataset

`btcusdt_1h_20240705_20241231_binance_spot` — 4320 barras 1h.

## Métricas

### Baseline (custos H.1)

| Métrica        |    Valor |
| -------------- | -------: |
| final_equity   |  9959.83 |
| total_pnl      |   −40.17 |
| trade_count    |       58 |
| hit_rate       |   58.62% |
| max_drawdown   |    3.65% |

### Cost stress

| Cenário   | final_equity | Δ vs baseline |
| --------- | -----------: | ------------: |
| baseline  |      9959.83 |             — |
| fee+10    |      9728.15 |       −231.68 |
| slip+10   |      9913.45 |        −46.38 |
| spread+10 |      9728.15 |       −231.68 |

`fee+10 ≡ spread+10 = 9728.15` (ADR-0019 33ª confirmação).

### Monte Carlo

- p5  = 9595.53
- p50 = 10016.13
- p95 = 10357.39

## Sweep O.1 ↔ N.2 ↔ O.2 (BTC 1h 2024-H2, mesmo dataset)

| Configuração RSI | trades | hit | fe | MC p5 | spread ratio | decisão |
| ---------------- | -----: | ---: | -: | ----: | -----------: | ------- |
| 7/25/75 (O.1)    |    147 | 59.86% | 10128.01 | 9931.16 | **0.9418** | **fail** |
| **14/30/70 (N.2)** | **64** | **67.19%** | **10117.99** | **9878.93** | **0.9747** | **canary_only** |
| 21/35/65 (O.2)   |     58 | 58.62% |  9959.83 | 9595.53 | 0.9767 | canary_only |

**Sweet spot paramétrico = N.2 (padrão).** Nenhuma configuração domina 14/30/70
em todos os eixos — hit + fe + critério 3. O.1 perde Critério 3; O.2 perde hit
e MC p5.
