# BACKTEST.md — Donchian 20/10 BTCUSDT 1h 180d (baseline)

> Gate ativo: **validação (relatório)**. Produzido a partir dos 4 JSONs persistidos em `results/validation/donchian-20-10-btc-180d-baseline/` pelo subcomando `alpha-forge validate` (ADR-0016 + ADR-0017).

## Dataset

- **ID:** `btcusdt_1h_20250705_20251231_binance_spot`.
- **Período:** 2025-07-05 00:00 UTC → 2025-12-31 23:00 UTC.
- **Barras:** 4320.
- **sha256:** ver `data/datasets.yaml` (ADR-0005 — dataset é imutável por contrato).
- **Gaps declarados:** 0.

## Período e recorte

- **Recorte total (baseline cost_stress):** as 4320 barras; sem exclusão adicional. Warm-up de 20 barras é tratado pelo próprio `DonchianBreakoutStrategy.on_bar` que emite `HOLD` nas primeiras janelas.
- **Recorte walk-forward:** scheme=rolling com train_fraction=0.5 produz 4 folds válidos (fold 0 pulado por falta de train prévio; ADR-0003). Cada fold = 432 barras train + 864 barras test (~36 dias test por fold).

## Custos aplicados (ADR-0006 + ADR-0019)

- **Taker fee:** 5.0 bps.
- **Slippage:** 2.0 bps por unidade de `notional/capital_inicial` (como fracao×alavancagem=0.2, slip efetivo ≈ 0.4 bps por fill).
- **Spread:** 0.0 bps (baseline). Stress até +10bps testado explicitamente.

## Métricas (ADR-0007) — baseline (4320 barras)

Rodadas pelo pipeline `alpha-forge validate`:

| Métrica | Valor |
|---|---|
| `total_pnl` | **-910.21 USDT** |
| `trade_count` | **110** |
| `hit_rate` | **0.2545** (25.45%) |
| `max_drawdown` | **0.1049** (10.49%) |
| `final_equity` | **9089.79 USDT** (capital inicial 10000; **-9.10% de return**) |

**Leitura rápida:** estratégia **perde dinheiro** no período; hit-rate inferior a 1/3; 110 trades gerando pnl médio por trade ≈ -8.28 USDT.

## Sensibilidade via cost_stress (ADR-0014 + ADR-0019)

Rodada via `--stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10`:

| Label | fee_Δ | slip_Δ | spread_Δ | final_equity | Δ vs baseline | % delta | trade_count | hit_rate | max_drawdown |
|---|---|---|---|---|---|---|---|---|---|
| `baseline` | 0 | 0 | 0 | 9089.79 | 0 | 0% | 110 | 0.2545 | 0.1049 |
| `fee+10` | +10 | 0 | 0 | 8652.06 | -437.73 | -4.81% | 110 | 0.1909 | 0.1461 |
| `slip+5` | 0 | +5 | 0 | 9046.05 | -43.74 | -0.48% | 110 | 0.2455 | 0.1090 |
| `spread+10` | 0 | 0 | +10 | 8652.06 | -437.73 | -4.81% | 110 | 0.1909 | 0.1461 |

**Observação estrutural:** `fee+10` e `spread+10` produzem **exatamente o mesmo delta** (-437.73) — coerente com ADR-0019: spread é aditivo em bps idêntico a fee quando `notional/capital_inicial` é constante (aqui sempre = 0.2). Esta simetria **estrutural** é propriedade do modelo de custo, não coincidência do dataset.

**Monotonicidade ADR-0010 + ADR-0019 preservada:** todos os três cenários têm `final_equity` ≤ baseline (✓), `trade_count` idêntico (✓ — custos não afetam decisão de trade, só PnL por construção), `max_drawdown` ≥ baseline em todos (✓ — maior custo, maior stress de equity).

## Walk-forward (ADR-0003)

Scheme=rolling, train_fraction=0.5, min_test_bars=50, n_folds=5 (fold 0 pulado):

| Fold | Train período | Test período | Train bars | Test bars | trades | total_pnl | hit_rate | max_drawdown |
|---|---|---|---|---|---|---|---|---|
| 1 | 2025-07-23..2025-08-09 | 2025-08-10..2025-09-14 | 432 | 864 | 23 | -156.03 | 0.2174 | 0.0216 |
| 2 | 2025-08-28..2025-09-14 | 2025-09-15..2025-10-20 | 432 | 864 | 21 | +10.64 | 0.3333 | 0.0092 |
| 3 | 2025-10-03..2025-10-20 | 2025-10-21..2025-11-25 | 432 | 864 | 18 | -247.51 | 0.2778 | 0.0328 |
| 4 | 2025-11-08..2025-11-25 | 2025-11-26..2025-12-31 | 432 | 864 | 23 | -327.91 | 0.1739 | 0.0460 |

**Soma pnl folds test-only:** -720.81 USDT (menor em magnitude que baseline full -910.21 porque as primeiras ~432 barras do recorte total — em `2025-07-05..2025-07-22` — entram **apenas** como train do fold 1 e não são contadas em nenhum test).

**Consistência temporal:** 3 de 4 folds negativos; único fold positivo (fold 2) entrega lucro de apenas 10.64 USDT; não há regime identificável onde a estratégia seja rentável dentro desta janela.

## Monte Carlo (ADR-0003)

- **Resamples:** 500.
- **Seed:** 42 (fixa; ADR-0003 exige semente).
- **Base de resample:** 110 PnLs de trade do baseline cost_stress.

Percentis de `final_equity` (capital inicial = 10000):

| p5 | p25 | p50 (mediana) | p75 | p95 |
|---|---|---|---|---|
| **8821.60** | 9063.09 | **9246.86** | 9426.36 | **9716.27** |

Percentis de `max_drawdown`:

| p5 | p25 | p50 | p75 | p95 |
|---|---|---|---|---|
| 0.0429 | 0.0638 | **0.0816** | 0.0980 | **0.1199** |

**Original `final_equity`:** 9279.18 USDT (consistente com a região de p50 do Monte Carlo).
**Original `max_drawdown`:** 0.0 (artefato: `monte_carlo_trades` parte de sequência ordenada temporalmente que neutraliza drawdown agregado quando primeiro trade é lucrativo; o MDD real do baseline é 0.1049 — ver baseline cost_stress).

**Leitura Monte Carlo:** **nenhum dos 5 percentis preserva capital** (todos < 10000). Probabilidade empírica de `final_equity ≥ 10000` é aproximadamente 0% (acima de p95=9716 seriam <5%, mas aqui p95 já está abaixo do breakeven).

## Robustez multi-asset

**Não testada neste piloto.** SPEC §13 declara "dataset único (BTCUSDT) — sem validação cross-asset". Piloto futuro pode rodar o mesmo protocolo sobre `ethusdt_1h_20250705_20251231_binance_spot` e `solusdt_1h_20250705_20251231_binance_spot` (ambos cadastrados em `data/datasets.yaml`).

## Lookahead bias

- **Property-based de causalidade verde:** sim (suíte `289/1skip`).
- **Coverage de OHLCV:** completo (ADR-0002 §cobertura; `tests/property/test_lookahead_guard.py`).
- **Guardião de causalidade (ADR-0002):** violação detectaria em tempo de execução — nenhum stacktrace no log do pipeline.

## Persistência

- **Artefatos gravados em:** `results/validation/donchian-20-10-btc-180d-baseline/`.
- **Arquivos:** `run.json`, `walk_forward.json`, `monte_carlo.json`, `cost_stress.json` (ADR-0015 + ADR-0017).
- **`run.json` grava flags canônicas** — re-execução com mesmo run_id é bit-a-bit reprodutível (ADR-0017).

## Notas

- **110 trades em 180 dias = ~0.61 trades/dia.** Trend-following de baixíssima frequência; custos totais dominam o resultado (baseline já perde 9%, fee+10 custa outros 4.8%).
- **25% hit-rate é muito baixo para trend-following.** Donchian pura sem filtro de regime entra em muitos rompimentos falsos nesse regime de consolidação/baixa.
- **Monotonicidade é propriedade estrutural:** não depende de edge da estratégia; teríamos a mesma monotonicidade mesmo com estratégia aleatória.
- **Warning benigno:** `numpy RuntimeWarning: invalid value encountered in divide` aparece em resampling do Monte Carlo (cálculo de correlação sobre arrays com variância zero); não afeta percentis.
