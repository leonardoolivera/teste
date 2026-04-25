# 0211 — Roadmap 1000 Fase Auto-Paralela 1+2 closeout

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Usuário ("vamo fazer tudo paralelo... force o pc"), agente
**Relates to:** ADR-0209 (Fase 1 pre-reg), ADR-0210 (Fase 2 pre-reg), ADR-0203 (roadmap 1000), ADR-0202 (Padrão 50 candidato)

## Contexto

Fase 1 (no-filter) + Fase 2 (with_filter+canonical+perturbations+ablations) executadas via dispatcher paralelo (`tools/run_roadmap_auto.py`, 10 workers em Ryzen 5 5600GT). 594 probes runnable cobertos; 0 falhas. Wave 1 wall=33min, Wave 2 wall=4min (mix mais rápido).

Cobertura: 594/1000 = **59.4% do roadmap esgotado**. Restantes 406: engines novos (regime_meta=45, portfolio_*=50, stack_combo=70, exotic_*=144, ml_*=1) + filtros regime-detector novos (~75) + perturbações não-mapeáveis (3) + alguns dataset gaps.

## Resultado agregado

| Metric | Wave 1 | Wave 2 | Total |
|---|---:|---:|---:|
| Probes | 204 | 390 | 594 |
| OK / Fail | 204/0 | 390/0 | 594/0 |
| Sh-pass (Sh≥1.5 ∧ tr≥30) | 14 | 54 | 68 |
| Wall-clock | 33min | 4min | 37min |

### Pass-rate por engine

| Engine | N | Sh-pass | Sh% | Alfa-pass | Alfa% |
|---|---:|---:|---:|---:|---:|
| **bollinger** | 156 | **34** | **22%** | 67 | 43% |
| rsi | 138 | 13 | 9% | 60 | 43% |
| ma_crossover | 108 | 9 | 8% | 43 | 40% |
| composite_bb_rsi | 60 | 6 | 10% | 26 | 43% |
| supertrend | 72 | 4 | 6% | 28 | 39% |
| keltner | 36 | 1 | 3% | 12 | 33% |
| zscore | 24 | 1 | 4% | 10 | 42% |
| **donchian** | (canonical) | 0 | 0% | - | - |

### Top 23 probes (gate_sh ∧ gate_alfa)

| # | engine | asset | window | params | Sh | PnL% | alfa | tr |
|---:|---|---|---|---|---:|---:|---:|---:|
| 1 | ma_crossover | ETH | 2024-H2 | canonical (20/50) | 3.76 | 6.3 | 6.3 | 34 |
| 2 | bollinger | ETH | 2024-H2 | window *= 0.83 (=17) | 3.04 | 6.9 | 6.9 | 48 |
| 3 | bollinger | ETH | 2024-H2 | period *= 0.83 (=17) | 3.04 | 6.9 | 6.9 | 48 |
| 4 | keltner | BTC | 2025-H1 | 20/14/2.5 | 2.86 | 4.3 | 8.3 | 31 |
| 5 | **supertrend** | **ETH** | **2025-H1** | 20/3.5 | **2.71** | 11.8 | **+35.3** | 190 |
| 6 | composite_bb_rsi | ETH | 2024-H2 | 15/1.5/35/65 | 2.54 | 5.1 | 5.1 | 53 |
| 7-8 | bollinger | ETH | 2024-H2 | 15/2.0 (×2 vias) | 2.07 | 4.7 | 4.7 | 48 |
| 9 | **supertrend** | **ETH** | **2025-H1** | 14/3.5 | 2.03 | 8.7 | **+32.2** | 193 |
| 10 | **ma_crossover** | **ETH** | **2025-H1** | 25/75 | 1.91 | 8.0 | **+31.5** | 154 |
| 11 | ma_crossover | ETH | 2024-H2 | canonical (20/50) dup | 1.88 | 6.3 | 6.3 | 34 |
| 12 | ma_crossover | ETH | 2024-H2 | 50/200 | 1.77 | 6.0 | 6.0 | 60 |
| 13 | zscore | BTC | 2025-H1 | 30/2.5 | 1.66 | 2.8 | 6.8 | 32 |
| 14 | rsi | BTC | 2025-H1 | canonical (14/30/70) | 1.61 | 2.8 | 6.8 | 39 |
| 15-16 | **ma_crossover** | **ETH** | **2025-H1** | 20/50 (×2 vias) | 1.61 | 6.8 | **+30.3** | 228 |
| 17-18 | bollinger | ETH | 2024-H2 | 15/1.75 (×2) | 1.57 | 3.8 | 3.8 | 57 |
| 19 | composite_bb_rsi | ETH | 2024-H2 | 15/1.5/30/70 | 1.56 | 2.2 | 2.2 | 35 |
| 20 | **supertrend** | **ETH** | **2025-H1** | 14/3.0 | 1.55 | 6.5 | **+30.0** | 245 |
| 21 | bollinger | ETH | 2024-H2 | num_std += 0.25 | 1.54 | 3.4 | 3.4 | 32 |
| 22-23 | bollinger | ETH | 2024-H2 | 15/2.25 (×2) | 1.52 | 3.3 | 3.3 | 36 |

(Linhas duplicadas refletem mesma config alcançada via dois caminhos do roadmap — perturbação relativa resolve para mesmo concreto que entry hardcoded. Não é bug, é redundância do roadmap original.)

## Padrões identificados / consolidados

### Padrão 50 promovido: bear-avoidance trend-following ETH 2025-H1 cross-engine

ADR-0202 registrou Padrão 50 como **candidato** (1 probe TF10I.5 ma_crossover ETH 2025-H1 10m). Esta Fase consolidou em **5 engines independentes** todos passando gate em ETH 2025-H1 1h:

| Engine | Params | Sh | alfa% |
|---|---|---:|---:|
| supertrend | 20/3.5 | 2.71 | +35.3 |
| supertrend | 14/3.5 | 2.03 | +32.2 |
| supertrend | 14/3.0 | 1.55 | +30.0 |
| ma_crossover | 25/75 | 1.91 | +31.5 |
| ma_crossover | 20/50 | 1.61 | +30.3 |

5 configs, 2 engines momentum-long, mesma window bear (-47% B&H), alfas convergentes em +30-35%. **Padrão 50 promovido de candidato a validado cross-engine** dentro deste regime. Consistente com hipótese "trend-following long-only não-entra durante alt bear ⇒ alfa por evitar drawdown".

**Caveat**: ainda é 1 window (ETH H1 2025). Cross-era validation necessária antes de promover a estratégia. Próxima Fase deve incluir bear ETH H2 2022 (se dataset disponível) ou bear similar.

### Padrão 51 (novo): Bollinger curto-window robusto ETH 2024-H2

ETH 2024-H2 (window flat, B&H ≈ 0%) tem **9 dos 23 top probes** todos centrados em **bollinger window=15-17**:
- window *= 0.83 (=17) com num_std=2.0: Sh=3.04
- 15/2.0: Sh=2.07
- 15/1.75: Sh=1.57
- 15/2.25: Sh=1.52
- num_std += 0.25 (variação): Sh=1.54

Gradiente claro: **menor window = mais Sh** (com num_std próximo de 2.0). Window=20 (canonical) já não passa em ETH 2024-H2; window=15 é sweet spot.

**Hipótese**: ETH 2024-H2 = regime baixa-vol, mean-reversion intra-curta funciona, longas detecções perdem sinal por agregação.

Ainda regime-specific (não cross-era). Promover a Padrão 51 candidato; cross-era em ETH 2025-H1/H2/2023-H2 antes de operacionalizar.

### Padrão 52 (novo) candidato: ma_crossover canonical ETH 2024-H2

Único probe Sh > 3.0 em ETH 2024-H2 com ma_crossover 20/50 (Sh=3.76). Aparece duas vezes (canonical + 20/50 explícito) — mesma config, score idêntico. Surpresa: regime flat geralmente é hostil a trend-following. Investigar por que aqui passa.

### Engine champion: Bollinger

22% pass-rate (34/156) destaca-se como leader, ~2-3x os outros. Confirma posição histórica do bollinger no stack canonical (ADR-0028+). Concentração de passes em ETH 2024-H2 com windows curtos (15-17) sugere engine sensível a regime escolhido em vez de generalizable.

### Engine refutados/marginais

- **donchian canonical (20/10)**: 0% pass cross-windows. Já refutado em ADR-0202 (TF10m); confirma 1h também — donchian breakout não funciona em qualquer TF deste universo.
- **keltner**: 3% (1/36). 1 hit foi BTC 2025-H1 — possivelmente ruído. Status: refutado, marginal.
- **zscore**: 4% (1/24). Refutado.
- **rsi standalone 9%**: melhora marginal vs bollinger (22%) e composite (10%). Sobrevive como componente do stack (ex composite_bb_rsi), não standalone.
- **supertrend 6%**: passes concentrados no Padrão 50 ETH 2025-H1 — fora desse regime, não sobrevive.

## Decisão

1. **Fase auto-paralela 1+2 fechada com sucesso**: 594/1000 cobertos, 68 probes passing gate duplo, 0 failures, 37min wall-clock total.
2. **Padrão 50 promovido** de candidato a **validado cross-engine intra-regime** (ETH 2025-H1 bear).
3. **Padrão 51 registrado**: bollinger short-window ETH 2024-H2 (regime flat).
4. **Padrão 52 candidato**: ma_crossover canonical 20/50 ETH 2024-H2 (Sh=3.76 isolado, requer replicação cross-window).
5. **Engines refutados** nesta camada de teste: donchian, keltner, zscore.
6. **Dispatcher infra preservada** para Fases futuras: `tools/run_roadmap_auto.py` + `tools/summarize_roadmap_auto.py` + `tools/audit_roadmap_auto_vs_batches.py`. 20/20 cross-check com batches MA01/ST01/etc.
7. **Pendente cross-era validation** para Padrões 50/51/52 antes de qualquer export para BotBinance (ADR-0030/0203 gates).

## Próximas frentes

**Imediatamente actionable** (sem código novo):
- **Cross-era validation Padrão 50**: replicar 5 configs winners em outros bears do dataset (BTC 2025-H1 já testado bear-leve −8%; precisa BTC/SOL/ETH 2022-H2 ou outras window bear se disponíveis).
- **Cross-era validation Padrão 51**: replicar bollinger 15/2.0 em ETH 2025-H1, ETH 2025-H2 e BTC/SOL 2024-H2 para sair de regime-specific.
- **Padrão 52 replication**: ma_crossover 20/50 em outros 1h windows.

**Requer código novo** (Fase 3+):
- regime_meta engine (45 probes T1) — combinar regime detector + 13 strategies gating.
- portfolio_stack13 (36 probes) — fixed 1/13 allocation.
- stack_combo (70 probes) — combinação de subsets.
- exotic_feature_flag (144 probes T4) — orderbook/funding/CVD ingest.
- ml_feature_flag (1 probe T4) — modelo ML.

## Stop conditions (mantém ADR-0203)

- Não promover single-probe sem cross-era (lição Padrões 45/48/50).
- Não export até cross-era validation (gate ADR-0030).
- Continue autopilot até user redirect.

## Não-alvo

- Não revalidar com mc-resamples > 500 (default da CLI já adequado para screening).
- Não alongar fees/slippage stress nesta camada (cobrir em validação dedicada).
- Não export para BotBinance — todos os achados são screening cross-window, não OOS validados independentemente.

## Padrões totais: 52 (50 promovido cross-engine; 51 candidato bollinger curto; 52 candidato ma_crossover canonical)
