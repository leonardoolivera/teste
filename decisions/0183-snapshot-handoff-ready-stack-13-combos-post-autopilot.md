# 0183 — Snapshot handoff-ready: stack 13 combos post-autopilot exhaustion

**Status:** Accepted — stack cristalizado, handoff v3 canonical.
**Date:** 2026-04-21
**Deciders:** Usuário (continuação autopilot) + agente
**Relates to:** ADR-0096 (snapshot 2026-04-20, este o atualiza), ADR-0030 (runtime faithful), ADR-0140 (última promoção), ADR-0172 (Keltner closeout + Padrão 45), ADR-0179 (autopilot pausa 1), ADR-0180-0182 (v4 pyramid ciclo), Padrões 20-47

## Propósito

Snapshot pós-autopilot 2026-04-20→2026-04-21. Atualiza ADR-0096 com:
- Todas refutações since (KE / ZS / TF15m / TF30m / CONS) — **zero promoções**
- Stack inalterado: **13 combos, 11 manifest files**, última promoção 2026-04-20 (SOL trend_htf 25/75 via ADR-0140)
- Infra v4 pyramid construída mas unused (stand-down ao bot)
- Fronteiras cheap research **exauridas** (diminishing returns confirmado Padrão 47)
- Estado = **handoff-ready** ao bot usando exclusivamente runtime faithful v3

## 1. Stack ativo inalterado desde 2026-04-20

13 combos em 11 manifest files (exports/approved/):

| Manifest file | Version | Combos | Status |
|---|---|---:|---|
| bollinger_width_regime_20260418.json | v1 | (deprecated) | superseded |
| bollinger_width_regime_20260418_v2.json | v2 | 4 long | active |
| bollinger_short_width_20260419.json | v3 | 4 short | active |
| rsi_short_width_20260419.json | v3 | (deprecated) | superseded |
| rsi_short_width_2025h1_20260419.json | v4a | 1 short | active |
| rsi_short_pure_2025h2_20260419.json | v4b pre | — | superseded |
| rsi_short_pure_2025h2_20260420.json | v4b | 2 short | active |
| rsi_short_pure_2025h2_20260420b.json | v4b corrigido | — | superseded |
| rsi_short_trendhtf_2025h1_sol_20260420.json | v6.1 | 1 short | active |
| rsi_long_width_eth_2024h2_20260420.json | v7 | 1 long | active |
| manifest.schema.json | schema | — | schema |

**13 combos: 5 long + 8 short.** (ADR-0096 tinha typo "9 short"; contagem atual 4+1+2+1 = 8 short.)

## 2. Refutações since 2026-04-20 (resumo)

| Série | ADR range | Runs | Pass | Conclusão |
|---|---|---:|---:|---|
| KE (Keltner) | 0170-0174 | 15 | 1/15 | Padrão 45 (ETH-only) |
| ZS (zscore MR) | 0175-0176 | 9 | 3/9 | decay cross-era |
| TF15m | 0177-0178 | 9 | 3/9 | era-específico (Padrão 46) |
| TF30m | 0179 | 9 | 1/9 | pior que 15m (Padrão 47) |
| CONS (BB short pyramid v4) | 0180-0182 | 3 | 1/3 | Padrão 45 re-confirmado |
| **Total since snapshot** | | **45** | **9/45** | zero promoções ao stack |

**Hit rate 9/45 = 20%** (vs gate ≥2/3 = 67%). Todas as frentes cheap single-session esgotadas.

## 3. Padrão 45 consolidado (N=3 engines)

"ETH 2025-H1 é outlier sistemático em engines mean-reversion/trend-following 1h crypto. Qualquer descoberta single-asset de Sh≥1.5 em ETH 2025-H1 *sem replicação em BTC E SOL na mesma janela* deve ser tratada como evidência de Padrão 41, não de edge estrutural."

Evidência: DE (trend_htf 1d), KE (Keltner), CONS (BB pyramid). 3 engines independentes, 3 famílias distintas.

Implicação operacional: **futuros pré-regs devem exigir cross-asset ≥2/3 desde Fase 1** (não relaxar para single-era) quando hipótese baseia-se em behavior ETH.

## 4. Infra v4 pyramid — preservada unused

ADR-0180 (runtime_contract `pyramid_equity_based`) + dev completo:
- `BollingerWidthFilter.max_width_bps` / `ATRRegimeFilter.max_atr_bps` opt-in
- `SizingMode.PYRAMID_EQUITY` + RiskBudget validators
- `_Tranche` stack + `_PyramidPosition` no engine
- CLI flags `--pyramid-*`
- 26/26 unit tests pass
- 3 runs CONS sem crash (funcional)

**Stand-down:** manifest v4 schema NÃO escrito. Bot notificado via bridge para cancelar ADR local adapter. Infra fica disponível para hipótese futura sem custo operacional (código dormente).

## 5. Estado handoff-ready

Todos critérios atendidos:
- ✅ Stack validado walk-forward + MC + cost_stress em 13 combos
- ✅ Runtime contract v3 faithful (ADR-0030, 5 invariantes literais)
- ✅ Manifests v3+ com `execution_hints`, `runtime_invariants`, `live_status`
- ✅ Exporter diag em `exports/diag/` (audit summaries)
- ✅ Bridge inbox atualizado com v4 stand-down

**Bot action path**: consumir os **9 manifest files active** listados §1, ignorar deprecated, paper-trade indefinido até user sinalizar live.

## 6. Decisão autopilot: pausa 2

- Padrão 47 reforçado: 45 runs 0 promoções = esgotamento estatístico
- Cheap frontiers **exauridas** (KE 4h / KE long-only previstas como diminishing returns; BB+trend_htf long non-alvo per ADR-0159)
- Frentes expansivas remanescentes (orderbook, cross-sectional, composite engines) requerem dev substancial + decisão explícita do user
- Autopilot **pausado formalmente pela 2ª vez** — user retorna com direção explícita se quiser retomar

## 7. Não-alvo (desta sessão)

- Não rodar novas probes cheap (esgotadas)
- Não escrever manifest v4 schema (stand-down)
- Não promover snapshot a "v6.2 bundle consolidado" (13 combos já estão em 9 manifest files; consolidar em um super-JSON adicionaria fragilidade sem ganho operacional)
- Não editar manifests v3 existentes (estáveis)

## 8. Ação executada nesta sessão (2026-04-20→21 ciclo completo)

- ✅ Verificado KE.10-12 gate (0/3, Keltner re-arquivado — já coberto por ADR-0172)
- ✅ Executado CONS.1-3 via runtime v4 pyramid (1/3 FAIL)
- ✅ ADR-0182 closeout CONS + Padrão 45 consolidado
- ✅ Bridge post v4 stand-down ao bot
- ✅ ADR-0183 (este) snapshot handoff-ready
- ✅ STATE.md atualizado

## 9. Próxima sessão — requer input user

Se retomar pesquisa, escolher entre:
- (A) Pyramid long-only + trend_htf (non-alvo per ADR-0159, mas não-testado empiricamente — prior revisado ~10%)
- (B) Composite engine BB+RSI (dev 2-4h, prior ~25%)
- (C) Portfolio / cross-sectional (dev ~1 dia, prior desconhecido)
- (D) Orderbook microstructure (alto custo, dataset não ingestado)
- (E) **Aceitar stack atual + bot paper-trade indefinido** (zero dev AF)

Sem input, autopilot permanece pausado.
