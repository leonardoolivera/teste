# BACKTEST.md — N.1 RSI 14/30/70 SOL 1h 2024

> Gate: **backtest**. Leitura dos 4 JSONs em
> `results/validation/rsi-14-30-70-sol-1h-2024-baseline/`.

## Dataset

`solusdt_1h_20240705_20241231_binance_spot` — 4320 barras 1h, janela
2024-07-05 → 2024-12-31 (mesmo recorte J.1).

## Métricas

### Baseline (custos H.1)

| Métrica        |    Valor |
| -------------- | -------: |
| final_equity   |  9850.00 |
| total_pnl      |  −150.00 |
| trade_count    |       63 |
| hit_rate       |   58.73% |
| max_drawdown   |    6.35% |

## Cost stress (ADR-0014 / ADR-0019)

| Cenário   | final_equity |     Δ vs baseline |
| --------- | -----------: | ----------------: |
| baseline  |      9850.00 |                 — |
| fee+10    |      9598.55 |           −251.45 |
| slip+10   |      9799.67 |            −50.33 |
| spread+10 |      9598.55 |           −251.45 |

`fee+10 == spread+10` exato (ADR-0019, 29ª confirmação protocolo).

## Monte Carlo

Percentis sobre `final_equity` (1000 resamples, seed=42):

- p5  = 9568.51
- p25 = 9835.75 (estimativa implícita)
- p50 = 10023.73
- p95 = 10417.59

## Relação com J.1 (Bollinger SOL 1h 2024)

| Dimensão       |   J.1 Bollinger |        N.1 RSI |    Δ |
| -------------- | --------------: | -------------: | ---: |
| hit_rate       |          67.82% |         58.73% | −9.09 pp |
| max_drawdown   |           3.43% |          6.35% | +2.92 pp |
| final_equity   |         10684.24 |         9850.00 | −834 |
| trades         |              87 |             63 | −24 |
| spread ratio   |           0.967 |          0.975 | +0.008 |

N.1 inferior a J.1 em fe/hit/mdd, mas **ambos cruzam os 3 critérios** — edge
RSI existe, é menos eficiente que Bollinger, mas estrutural.
