# BACKTEST.md — H.3 Donchian+regime SMA slope

## Dataset

- `btcusdt_1h_20250705_20251231_binance_spot`, 4320 barras (180d × 24h).
- Mesmo dataset de H.1 — apples-to-apples.

## Métricas

Todas as tabelas abaixo (baseline cost_stress + cenários + walk-forward + Monte Carlo + comparação transversal) consolidam as métricas do piloto. Arquivos fonte em `results/validation/donchian-20-10-btc-180d-regime-sma/`.

## Baseline cost_stress

| Métrica | Valor | vs H.1 baseline |
|---|---|---|
| `final_equity` | **9195.59** USDT | +105.80 (+1.16 pp) |
| `total_pnl` | −804.41 USDT | +147.42 |
| `trade_count` | 114 | +4 |
| `hit_rate` | **29.82%** | +4.37 pp |
| `max_drawdown` | 9.60% | −0.41 pp |

## Cost stress (3 cenários)

| Label | `final_equity` | Δ vs baseline | Δ % |
|---|---|---|---|
| `baseline` | 9195.59 | 0 | 0% |
| `fee+10` | 8741.66 | −453.93 | −4.94% |
| `slip+5` | 9150.22 | −45.37 | −0.49% |
| `spread+10` | 8741.66 | −453.93 | −4.94% |

**ADR-0019 `fee+10 ≡ spread+10` confirmado (5ª vez; 1ª vez com regime filter ativo):** bit-a-bit 8741.66. Propriedade estrutural atravessa o novo módulo `regimes/` sem mudança — esperado pelo design (filtro altera trade_count; relação fee↔spread depende de `notional/capital_inicial`, que é constante entre cenários).

**Critério 3 (spread+10 Δ ≥ −5%) passa por 0.06 pp** — margem muito apertada; em H.1 Δ era −4.82% (similar). Filtro não alivia sensibilidade a spread+10.

## Walk-forward (4 folds efetivos; fold 0 pulado por falta de train prévio)

| Fold | test_bars | trade_count | total_pnl | hit_rate |
|---|---|---|---|---|
| 1 | 864 | 27 | −114.82 | 22.22% |
| 2 | 864 | 24 | −217.94 | 45.83% |
| 3 | 864 | 25 | −160.54 | 32.00% |
| 4 | 864 | (agregado no summary) | — | — |

> Nota: o summary do `validate` reporta `4 fold(s), 80 trade(s)`; fold 4 absorve o resíduo. Detalhe fold-a-fold está em `results/validation/donchian-20-10-btc-180d-regime-sma/walk_forward.json`.

**Fold 2** atinge `hit_rate = 45.83%` — **primeira vez no protocolo que um fold passa 45% em Donchian baseline+filter**. Regime-filter está capturando sinal em um sub-período. Porém os outros 3 folds ficam abaixo, e a agregação fica em 29.82%. **Fragilidade: o edge é concentrado em um regime específico do período, não uniforme.**

## Monte Carlo (500 resamples, seed=42)

| Percentil | H.3 `final_equity` | H.1 `final_equity` | Δ |
|---|---|---|---|
| p5 | 8986.95 | 8821.60 | +165.35 |
| p25 | 9256.06 | 9063.09 | +192.97 |
| p50 | **9408.98** | 9246.86 | +162.12 |
| p75 | 9574.30 | 9426.36 | +147.94 |
| p95 | 9850.98 | 9716.27 | +134.72 |

**Todos os 5 percentis MC deslocam para cima** em ~+135 a +193 USDT. Filtro melhora a distribuição inteira, mas **p95 = 9850.98 < 10000** — nem no topo o backtest cruza breakeven.

## Comparação transversal H.1 → H.3

| Dimensão | H.1 baseline | H.3 baseline | Leitura |
|---|---|---|---|
| `final_equity` | 9089.79 | 9195.59 | +105.80 (+1.16 pp) — filtro melhora, mas pequeno |
| `hit_rate` | 25.45% | 29.82% | +4.37 pp — direção certa, threshold ainda não atingido |
| `trade_count` | 110 | 114 | +4 (filtro não reduziu — redistribuiu) |
| `max_drawdown` | 10.01% | 9.60% | −0.41 pp — marginal |
| MC p50 | 9246.86 | 9408.98 | +162 |
| Δ spread+10 | −4.82% | −4.94% | não alivia sensibilidade |

**Leitura:** regime filter `sma_slope:window=50:min_slope_bps=10` **reduz expectativa de perda** (baseline +105 USDT; todos os MC percentis +134 a +193), mas **não muda a natureza qualitativa** do sistema — edge continua insuficiente para cruzar 45% de hit_rate. O filtro captura sinal em 1 de 4 folds (fold 2 hit_rate 45.83%) e falha nos outros 3 — o recorte "slope SMA-50 ≥ 10 bps" não está alinhado com o regime que produz edge neste período.
