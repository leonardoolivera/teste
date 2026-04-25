# BACKTEST.md — H.4 Donchian+regime ATR

## Dataset

- `btcusdt_1h_20250705_20251231_binance_spot`, 4320 barras (180d × 24h).
- Idêntico a H.1 e H.3.

## Métricas

Todas as tabelas abaixo consolidam métricas do piloto. Arquivos fonte em `results/validation/donchian-20-10-btc-180d-regime-atr/`.

## Baseline cost_stress

| Métrica | H.4 Valor | vs H.3 | vs H.1 |
|---|---|---|---|
| `final_equity` | **9180.45** USDT | −15.14 (−0.16 pp) | +90.66 (+1.00 pp) |
| `total_pnl` | −819.55 USDT | −15.14 | +147.42 |
| `trade_count` | **72** | **−42** (37% fewer) | **−38** (35% fewer) |
| `hit_rate` | **26.39%** | −3.43 pp | +0.94 pp |
| `max_drawdown` | 8.80% | −0.80 pp | −1.21 pp |

## Cost stress (3 cenários)

| Label | `final_equity` | Δ vs baseline | Δ % |
|---|---|---|---|
| `baseline` | 9180.45 | 0 | 0% |
| `fee+10` | 8894.38 | −286.07 | **−3.12%** |
| `slip+5` | 9151.89 | −28.56 | −0.31% |
| `spread+10` | 8894.38 | −286.07 | **−3.12%** |

**ADR-0019 `fee+10 ≡ spread+10` (6ª confirmação):** bit-a-bit 8894.38.

**Critério 3 (spread+10 Δ ≥ −5%) passa com folga de 1.88 pp** — **maior folga em 5 pilotos**. H.1 foi −4.82%, H.3 foi −4.94%; H.4 é −3.12%. **Filtro ATR reduz trade_count o suficiente para aliviar sensibilidade a spread+10** (72 trades vs 110 em H.1 → 35% menos exposição agregada a spread). Este é o **primeiro sinal quantitativo** de que família de filtro escolhida importa para robustez a custos.

## Walk-forward (4 folds efetivos)

| Fold | test_bars | trade_count | total_pnl | hit_rate |
|---|---|---|---|---|
| 1 | 864 | 13 | −96.91 | 23.08% |
| 2 | 864 | 14 | −27.78 | 35.71% |
| 3 | 864 | 17 | −275.52 | 29.41% |
| 4 | 864 | 16 | −223.34 | 31.25% |

**Nenhum fold cruza 45%** (vs H.3 onde fold 2 atingia 45.83%). Dispersão menor entre folds (23-36% vs H.3 22-46%) — filtro ATR **homogeneíza** comportamento entre sub-períodos mas sem elevar o centro.

## Monte Carlo (500 resamples, seed=42)

| Percentil | H.4 `final_equity` | H.3 `final_equity` | H.1 `final_equity` | Δ H.4−H.1 | Δ H.4−H.3 |
|---|---|---|---|---|---|
| p5 | **9017.20** | 8986.95 | 8821.60 | **+195.60** | +30.26 |
| p25 | 9224.99 | 9256.06 | 9063.09 | +161.90 | −31.07 |
| p50 | 9371.52 | 9408.98 | 9246.86 | +124.67 | −37.46 |
| p75 | 9519.20 | 9574.30 | 9426.36 | +92.83 | −55.11 |
| p95 | 9804.17 | 9850.98 | 9716.27 | +87.90 | −46.81 |

**Padrão crítico:** H.4 vence H.1 em **todos os 5 percentis** (igual ao padrão de H.3). Mas H.4 **perde para H.3 em p25/p50/p75/p95** (−31 a −55) e **vence H.3 apenas em p5** (+30). **Interpretação:** ATR filter comprime a distribuição para cima no pior caso (p5 sobe mais que em H.3) mas a encolhe por cima (p95 cai). SMA filter produz distribuição com cauda direita mais longa (p95 mais alto); ATR produz distribuição mais concentrada (p5-p95 range = 787 USDT em H.4 vs 864 USDT em H.3).

**Nem H.3 p95 nem H.4 p95 cruza 10000.**

## Comparação transversal H.1 → H.3 → H.4 (três pilotos Donchian BTC 180d)

| Dimensão | H.1 (none) | H.3 (sma_slope) | H.4 (atr_regime) | Leitura |
|---|---|---|---|---|
| `final_equity` baseline | 9089.79 | 9195.59 | 9180.45 | H.3 > H.4 > H.1; diferença H.3↔H.4 marginal (−15). |
| `hit_rate` baseline | 25.45% | 29.82% | 26.39% | H.3 >> H.4 > H.1. **ATR não recupera hit_rate que SMA conseguiu.** |
| `trade_count` baseline | 110 | 114 | **72** | Só ATR reduz; SMA redistribuiu. |
| `max_drawdown` | 10.01% | 9.60% | 8.80% | Monotônico: mais filtro → menos drawdown. |
| MC p5 | 8821.60 | 8986.95 | **9017.20** | ATR vence no pior caso. |
| MC p50 | 9246.86 | **9408.98** | 9371.52 | SMA vence no centro. |
| MC p95 | 9716.27 | **9850.98** | 9804.17 | SMA vence no topo. |
| Δ spread+10 | −4.82% | −4.94% | **−3.12%** | **ATR reduz sensibilidade** a custos; SMA não. |
| Fold max hit_rate | 39.02% | **45.83%** | 35.71% | Só SMA cruza 45% em algum fold. |

**Leitura integrada:**

1. **Filtro ATR é qualitativamente diferente de SMA**, não apenas uma variação incremental. SMA **redistribui** trades sem reduzir número; ATR **corta** trades (−42 vs H.3). Consequência: ATR melhora robustez a custos (critério 3 com maior folga no protocolo) mas piora hit_rate.
2. **Nem slope nem ATR é suficiente isoladamente.** Ambos refutam critério 1. Hipótese combinada ("filtrar por slope AND por ATR") fica para H.5 se justificado.
3. **Trade-off revelado:** SMA maximiza centro da distribuição (p50, p95 altos); ATR maximiza cauda inferior (p5 alto) e minimiza custos. Se objetivo for **preservação de capital** (evitar quedas grandes), ATR é mais alinhado; se for **maximização do caso médio**, SMA. Este trade-off é informação nova trazida por H.4.
4. **ADR-0022 arquitetura 100% validada como contrato genérico.** 2 famílias de filtro plugam sem modificação de engine/validation/CLI dispatch. A infraestrutura está pronta para RSI-range, ADX-regime, HMM-2state sem nova ADR.
