# 0214 — V2/RAIO Ciclo 1 verdict — Padrões 50/51/52 cross-era + fee stress

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13 (anti-pergunta), em conformidade com escopo ADR-0213
**Relates to:** ADR-0211 (Padrões 50/51/52 V1), ADR-0212 (V1 closeout), ADR-0213 (V2+RAIO adoption pre-reg)

## Contexto

Ciclo 1 do V2/RAIO executou Top 4 ações pré-registradas em ADR-0213:
- **RB-ROOT-018** Execution invariant audit: 658/658 V1 runs clean → SURVIVOR.
- **PF-ROOT-001** + **PF-ROOT-023**: QUARANTINED por falta de equity-curve aggregation.
- **RM-ROOT-013**: PAUSED por requerer cross-asset filter engine novo.

Pivot autônomo (RAIO §13) para próximo nó alta-EV: **RB-ROOT-004 (cross-era validation) + RB-ROOT-007 (fee stress)** sobre os 3 padrões V1 quarentinados (P50/P51/P52). 9 configs × (6 cross-era + 2 fee stress) = 72 probes. Wall-clock 61s. Gate V2: Sh ≥ 1.0 ∧ trades ≥ 30.

## Resultados

### Padrão 50 (bear-avoidance trend ETH 2025-H1) — REFUTADO

5 configs V1 (supertrend 14/3.0, 14/3.5, 20/3.5; ma_crossover 20/50, 25/75) que passavam gate V1 em ETH 2025-H1:

| Config | Cross-era pass | Fee stress pass |
|---|---:|---:|
| supertrend 14/3.0 (P50-001) | 0/6 | 0/2 |
| supertrend 14/3.5 (P50-002) | 1/6 | 0/2 |
| supertrend 20/3.5 (P50-003) | 0/6 | 0/2 |
| ma_crossover 20/50 (P50-004) | 1/6 | 0/2 |
| ma_crossover 25/75 (P50-005) | 0/6 | 0/2 |
| **Total** | **2/30** | **0/10** |

**Critical finding (RB007 fee stress):** No baseline winner ETH 2025-H1, com fees 10bps (2x): Sh cai de +2.71 (V1, fees 5bps) para -1.51. Com fees 15bps (3x): Sh -1.70.

**Conclusão:** Padrão 50 era artefato de **fees baixos + single window**. Move-se para GRAVEYARD com `do_not_repeat_reason = "fee-fragile + single-window; baseline V1 fees 5bps inadequado pra screening"`. Lição metodológica: **screening V1 deveria ter usado fees 10bps default** (mais conservador).

### Padrão 51 (bollinger short-window ETH 2024-H2) — REFUTADO majoritariamente

3 configs V1 (window 15/2.0, 17/2.0, 15/1.75):

| Config | Cross-era pass | Fee stress pass |
|---|---:|---:|
| bollinger 15/2.0 (P51-001) | 1/6 (SOL 2024-H2) | 0/2 |
| bollinger 17/2.0 (P51-002) | 1/6 (SOL 2024-H2) | **2/2** |
| bollinger 15/1.75 (P51-003) | 1/6 (SOL 2024-H2) | 0/2 |
| **Total** | **3/18** | **2/6** |

**Observation:** Todos cross-era pass são SOL 2024-H2 — janela MR-friendly conhecida (Padrão 48). Não é generalização do P51, é re-detecção do P48. P51-002 (window=17) é único com fee resistance + cross-era passing → QUARANTINED para Sensitivity test (perturbação window vizinha).

P51-001 e P51-003 → GRAVEYARD. `do_not_repeat_reason = "single-window + cross-era SOL 2024-H2 explained by P48, not P51"`.

### Padrão 52 (ma_crossover canonical 20/50 ETH 2024-H2) — PROMISING

1 config V1 (ma_crossover 20/50):

| Window | Sh | tr | pnl% | Pass |
|---|---:|---:|---:|---|
| BTC 2024-H2 | 2.39 | 36 | 6.9 | **PASS** |
| SOL 2024-H2 | 1.22 | 32 | 4.8 | **PASS** |
| ETH 2025-H1 | -1.32 | 39 | -5.6 | fail |
| BTC 2025-H1 | -0.65 | 36 | -1.7 | fail |
| ETH 2025-H2 | -1.47 | 34 | -4.3 | fail |
| SOL 2025-H1 | -1.75 | 36 | -7.8 | fail |

**Cross-era: 2/6 (BTC + SOL 2024-H2)** — generalização cross-asset DENTRO de window 2024-H2. Não é regime-flat-asset-specific; é **regime-2024-H2 estrutural**.

**Fee stress (ETH 2024-H2 baseline):**
- fees 10bps (2x): Sh=1.67, tr=34, pnl=5.5%
- fees 15bps (3x): Sh=1.45, tr=34, pnl=4.8%

Sh cai de 3.76 → 1.67 → 1.45 (fees 5/10/15bps). Degradação ~58% do Sh inicial, mas mantém Sh > 1.0 + tr ≥ 30 em fees 3x. **Padrão 52 é fee-resistente**.

**Hipótese revisada:** ma_crossover 20/50 long-only captura algo estrutural do regime 2024-H2 (provavelmente low-vol/high-trend window onde MA cross funciona). Não é ETH-specific; é window-2024-H2 cross-asset.

**Decisão:** P52-Q-001 → **PROMISING** (RAIO Status). Próximo nível: 
- Sensitivity Test (RAIO Nível 3): perturbação local 18/55, 22/55, 18/45, 22/45.
- Cross-era além de 2024-H2 (se dataset ETH/BTC/SOL 2023-H2 ou 2024-H1 disponível).
- DSR/PSR para correção de data snooping (Padrão 52 é 1 hipótese promovida em 9 configs testadas; multiple comparison aceitável).

## Decisão

1. **Padrão 50 enterrado** com lição: V1 screening fees=5bps insuficiente; V2/RAIO adota fees=10bps default em screening próximo.
2. **Padrão 51 enterrado parcialmente** (P51-001, P51-003); P51-002 (window=17) movido para QUARANTINED com prior reduzido.
3. **Padrão 52 promovido a PROMISING** (não validado ainda) — único survivor da Top 4 com edge cross-asset + fee-resistente.
4. **Lição metodológica registrada:** fee=5bps em screening era subestimativa; V1 produziu falsos positivos em estratégias com `trades > N médio` onde fees acumulam. Mudar default V2 para fees=10bps em screening, reservar 5bps só para "best case" análise.

## Patterns updated

- ~~Padrão 50 cross-engine~~: REFUTADO; era artefato fees-low + single-window.
- Padrão 51: REFUTADO (P51-001, P51-003); P51-002 quarentinado.
- **Padrão 52: PROMISING** — ma_crossover 20/50 long-only, regime-2024-H2 cross-asset, fee-resistente.
- **Padrão 53 (novo): Screening fee floor**: backtests V1/V2 com fees<10bps produzem falsos positivos em estratégias high-turnover. Default screening = 10bps.
- Padrão 48 (consolidado, lição transversal): SOL 2024-H2 é MR-friendly regime-window; passes em SOL 2024-H2 raramente generalizam.

## Consequences

- **Positive:** RAIO entregou o critical filter que V1 não tinha. 1 padrão real promovido (52) e 2 falsos positivos (50, 51) cortados antes de virarem manifest. 72 probes em 61s confirma que infra V1 + critério V2 = combinação superior.
- **Negative:** Stack 13 atual baseado em padrões V1 pode conter outros falsos positivos análogos a Padrão 50 (fee-fragile high-turnover). Auditoria fee stress sobre os 13 manifests aprovados (`exports/approved/*.json`) recomendada antes de qualquer novo handoff BotBinance.
- **Neutral:** P51-002 quarentinado pode virar dead end ou survivor — Sensitivity vai resolver.

## Follow-ups

- ADR-0215 (próximo): RB007 fee stress sobre os 13 combos do stack canonical (manifests aprovados em produção). Análogo ao que foi feito para V1 winners. Dispatcher script ~50 LoC.
- Sensitivity test P52-001 (Nível 3): ma_crossover (18/45, 18/55, 22/45, 22/55) × (BTC, ETH, SOL × 2024-H2) = 12 probes.
- DSR/PSR sobre P52 family.
- Update HYPOTHESIS_TREE, NODE_LOG, SEARCH_STATE, GRAVEYARD com decisões deste ADR.

## Não-alvo

- Não promover P52 a Survivor sem Nível 3 Sensitivity completo.
- Não rerodar Padrão 50 em variantes para tentar "salvar" — Graveyard é Graveyard (RAIO §6).
- Não export para BotBinance até Padrão 52 atinge Nível 5 Portfolio Integration + ADR.
- Não relaxar gate V2 (Sh ≥ 1.0) para "salvar" mais probes.
