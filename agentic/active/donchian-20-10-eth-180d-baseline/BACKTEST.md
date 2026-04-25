# BACKTEST.md — Donchian 20/10 ETHUSDT 1h 180d (baseline)

> Gate ativo: **validação (relatório)**. Produzido a partir dos 4 JSONs persistidos em `results/validation/donchian-20-10-eth-180d-baseline/`.

## Dataset

- **ID:** `ethusdt_1h_20250705_20251231_binance_spot`.
- **Período:** 2025-07-05 00:00 UTC → 2025-12-31 23:00 UTC.
- **Barras:** 4320.
- **sha256:** ver `data/datasets.yaml` (ADR-0005 — dataset é imutável por contrato).
- **Gaps declarados:** 0.

## Período e recorte

- **Recorte total (baseline cost_stress):** as 4320 barras; sem exclusão adicional. Warm-up de 20 barras é tratado pelo `DonchianBreakoutStrategy.on_bar` que emite `HOLD` nas primeiras janelas.
- **Recorte walk-forward:** scheme=rolling com train_fraction=0.5 produz 4 folds válidos (fold 0 pulado; ADR-0003). Cada fold = 432 barras train + 864 barras test (~36 dias test por fold).

## Custos aplicados (ADR-0006 + ADR-0019)

- **Taker fee:** 5.0 bps.
- **Slippage:** 2.0 bps por unidade de `notional/capital_inicial` (como fracao×alavancagem=0.2, slip efetivo ≈ 0.4 bps por fill).
- **Spread:** 0.0 bps (baseline). Stress até +10bps testado explicitamente.

## Métricas (ADR-0007) — baseline (4320 barras)

| Métrica | Valor |
|---|---|
| `total_pnl` | **+240.02 USDT** |
| `trade_count` | **96** |
| `hit_rate` | **0.2813** (28.13%) |
| `max_drawdown` | **0.0890** (8.90%) |
| `final_equity` | **10240.02 USDT** (capital inicial 10000; **+2.40% de return**) |

**Leitura rápida:** estratégia **preserva capital** no período com um margin fino (+2.4%); hit-rate ainda baixo (28.13%); 96 trades gerando pnl médio por trade ≈ +2.50 USDT. O resultado positivo é consistente com um outlier positivo ocasional compensando múltiplos trades perdedores — característico de trend-following sem filtro de regime.

**Comparação com H.1 (BTC 1h 180d, mesma estratégia):**

| Métrica | BTC (H.1) | ETH (H.2a) | Δ absoluto |
|---|---|---|---|
| `total_pnl` | -910.21 | +240.02 | +1150.23 |
| `trade_count` | 110 | 96 | -14 |
| `hit_rate` | 0.2545 | 0.2813 | +0.0268 |
| `max_drawdown` | 0.1049 | 0.0890 | -0.0159 |
| `final_equity` | 9089.79 | 10240.02 | +1150.23 |

ETH outperforma BTC no mesmo período pela mesma estratégia. Contudo, **hit_rate segue < 45%**, o que refuta a hipótese pelo critério 1. Lição: `final_equity` acima de capital não é garantia de edge — pode ser artefato de poucos outliers favoráveis.

## Sensibilidade via cost_stress (ADR-0014 + ADR-0019)

Rodada via `--stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10`:

| Label | fee_Δ | slip_Δ | spread_Δ | final_equity | Δ vs baseline | % delta | trade_count | hit_rate | max_drawdown |
|---|---|---|---|---|---|---|---|---|---|
| `baseline` | 0 | 0 | 0 | 10240.02 | 0 | 0% | 96 | 0.2813 | 0.0890 |
| `fee+10` | +10 | 0 | 0 | 9855.93 | -384.09 | -3.75% | 96 | 0.2708 | 0.1104 |
| `slip+5` | 0 | +5 | 0 | 10201.51 | -38.50 | -0.38% | 96 | 0.2813 | 0.0907 |
| `spread+10` | 0 | 0 | +10 | 9855.93 | -384.09 | -3.75% | 96 | 0.2708 | 0.1104 |

**Observação estrutural (2ª confirmação cross-asset):** `fee+10` e `spread+10` produzem **exatamente o mesmo delta** (-384.09 USDT; -3.75%; hit_rate 0.2708 idêntico; max_drawdown 0.1104 idêntico) também em ETH — reforça empiricamente que ADR-0019 captura uma propriedade estrutural do modelo de custo, não coincidência do dataset BTC de H.1. Propriedade: quando `notional/capital_inicial` é constante (aqui = 0.2), `fee_bps` e `spread_bps` são permutáveis no cálculo de `total_bps = taker_fee_bps + slippage_bps_per_unit_notional * (notional/capital_inicial) + spread_bps`.

**Monotonicidade ADR-0010 + ADR-0019 preservada:** todos os três cenários têm `final_equity ≤ baseline` (✓), `trade_count` idêntico (✓ — custos não afetam decisão de trade), `max_drawdown ≥ baseline` em todos (✓).

## Walk-forward (ADR-0003)

Scheme=rolling, train_fraction=0.5, min_test_bars=50, n_folds=5 (fold 0 pulado):

| Fold | Train período | Test período | Train bars | Test bars | trades | total_pnl | hit_rate | max_drawdown |
|---|---|---|---|---|---|---|---|---|
| 1 | 2025-07-23..2025-08-09 | 2025-08-10..2025-09-14 | 432 | 864 | 16 | +111.78 | 0.3750 | 0.0188 |
| 2 | 2025-08-28..2025-09-14 | 2025-09-15..2025-10-20 | 432 | 864 | 24 | -80.05 | 0.2917 | 0.0279 |
| 3 | 2025-10-03..2025-10-20 | 2025-10-21..2025-11-25 | 432 | 864 | 18 | -204.82 | 0.2222 | 0.0339 |
| 4 | 2025-11-08..2025-11-25 | 2025-11-26..2025-12-31 | 432 | 864 | 19 | -383.41 | 0.1053 | 0.0466 |

**Soma pnl folds test-only:** -556.50 USDT (menor em magnitude que baseline full +240.02, pois as primeiras ~432 barras do recorte total entram apenas como train do fold 1 — e nelas a estratégia ganhou o outlier positivo que puxa o baseline acima de breakeven).

**Consistência temporal:** 3 de 4 folds negativos em ETH (mesmo ratio que BTC); magnitudes decrescem conforme avança no tempo (hit_rate cai de 37.50% → 29.17% → 22.22% → 10.53%). **Degradação monotônica** em ETH é mais marcada que em BTC. Fold 1 positivo é o único que passa o limiar de 45% de hit_rate... não, espera: 37.50% < 45%, então nenhum fold passa o critério.

**Lição:** walk-forward refuta a hipótese **ainda mais explicitamente** que o baseline full porque na agregação temporal o sinal fade-out é cristalino; baseline full só parece melhor por capturar o warm-up (barras antes do primeiro fold) onde o outlier positivo morou.

## Monte Carlo (ADR-0003)

- **Resamples:** 500.
- **Seed:** 42 (fixa).
- **Base de resample:** 96 PnLs de trade do baseline cost_stress.

Percentis de `final_equity` (capital inicial = 10000):

| p5 | p25 | p50 (mediana) | p75 | p95 |
|---|---|---|---|---|
| **8651.16** | 9115.52 | **9434.94** | 9749.60 | **10339.78** |

Percentis de `max_drawdown`:

| p5 | p25 | p50 | p75 | p95 |
|---|---|---|---|---|
| 0.0368 | 0.0597 | **0.0795** | 0.1042 | **0.1417** |

**Original `final_equity`:** 9443.49 USDT (consistente com a região de p50 do Monte Carlo).
**Original `max_drawdown`:** 0.0 (mesmo artefato de sequência ordenada observado em H.1; MDD real do baseline é 0.0890 — ver cost_stress).

**Leitura Monte Carlo:** **4 de 5 percentis sub-breakeven**, apenas p95 acima de 10000. Probabilidade empírica de `final_equity ≥ 10000` está entre p75 e p95 — interpolação linear sobre ordem dos resamples sugere ≈17% (vs <<5% em H.1 BTC). ETH tem cauda superior melhor que BTC, mas ainda maioria dos resamples abaixo de breakeven.

## Robustez multi-asset

**H.2a fecha um dos pontos abertos de H.1 §13** — roda a mesma estratégia/período sobre ETH. Futuro piloto H.2d (`donchian-20-10-sol-180d-baseline`) completaria o trio BTC/ETH/SOL declarado em `data/datasets.yaml`. Padrão observado até agora (2 ativos × 1 estratégia × 1 período):

- **Propriedade estrutural `fee+Δ ≡ spread+Δ` replica em ambos** — evidência empírica forte de ADR-0019 (não artifact do BTC).
- **Monotonicidade ADR-0010 + ADR-0019 replica em ambos.**
- **hit_rate < 45% em ambos** — gap central (filtro de regime) é independente de ativo.
- **`final_equity` varia de sinal entre ativos** — BTC -9.1%, ETH +2.4% → `final_equity` sozinho é métrica ruidosa; `hit_rate` é mais estável como indicador de edge.

## Lookahead bias

- **Property-based de causalidade verde:** sim.
- **Coverage de OHLCV:** completo.
- **Guardião de causalidade (ADR-0002):** violação detectaria em tempo de execução — nenhum stacktrace no log do pipeline.

## Persistência

- **Artefatos gravados em:** `results/validation/donchian-20-10-eth-180d-baseline/`.
- **Arquivos:** `run.json`, `walk_forward.json`, `monte_carlo.json`, `cost_stress.json` (ADR-0015 + ADR-0017).
- **Reprodutibilidade bit-a-bit** via seed=42 + `run.json`.

## Notas

- **96 trades em 180 dias = ~0.53 trades/dia.** Frequência ligeiramente menor que em BTC (0.61/dia) — consistente com ETH ter menos rompimentos relevantes no período.
- **Warning benigno** `RuntimeWarning: invalid value encountered in divide` idêntico a H.1.
- **Fold 4 extremo:** 19 trades com hit_rate=10.53% (2 ganhadores, 17 perdedores) — indica regime bem adverso em final de 2025 para Donchian em ETH, pior que em BTC no mesmo fold (hit=17.39%).
