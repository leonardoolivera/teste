# 0038 — Re-derivação 3D de sensibilidade Bollinger com regime params corretos (reruns BK/BN/BO)

**Status:** Accepted
**Date:** 2026-04-19
**Deciders:** Agente AF (re-execução pós ADR-0037).
**Scope:** Substitui numericamente ADRs 0032/0033/0035. A regra `weakest_wins` (ADR-0034) permanece válida, mas aplicada sobre novas classes.

## Context

ADR-0037 documentou bug nos scripts BK/BN/BO: regime filter hardcoded em `(window=20, num_std=2)` quando manifest aprovado v2 declara `(window=30, num_std=1.5)`. 24 pilotos re-rodados com params corretos. Summary em `exports/diag/{bk,bn,bo}_rerun_summary.json`.

Gates strict idênticos aos originais: `trades ≥ 30, Sharpe ≥ 1.0, MDD ≤ 20%, PnL > 0, cost_stress_ratio_min ≥ 0.95, MC p5 final_equity > 10000, MC MDD p95 ≤ 10%`. `cost_stress_ratio` = `final_equity_stress / final_equity_baseline` (mesmo cálculo dos summaries originais).

## Resultados

### Série BK (num_std ±20% do baseline 1.5)

| Tag | Combo | ns | trd | Sh | MDD% | PnL% | cost_r | MCp5 | MCmdd95% | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| BK.1 | ETH 2024-H1 | 1.25 | 41 | 2.91 | 1.77 | +7.53 | 0.9810 | 10321 | 2.70 | **PASS** |
| BK.2 | ETH 2025-H1 | 1.25 | 41 | 1.19 | 4.25 | +3.88 | 0.9758 | 9732 | 6.03 | FAIL (MCp5) |
| BK.3 | BTC 2024-H2 | 1.25 | 27 | 0.98 | 2.46 | +1.37 | 0.9857 | 9797 | 3.66 | FAIL (trades, Sharpe, MCp5) |
| BK.4 | SOL 2024-H2 | 1.25 | 56 | 2.15 | 4.54 | +7.00 | 0.9736 | 10106 | 4.83 | **PASS** |
| BK.5 | ETH 2024-H1 | 1.75 | 32 | 0.75 | 3.58 | +1.92 | 0.9847 | 9797 | 4.56 | FAIL (Sharpe, MCp5) |
| BK.6 | ETH 2025-H1 | 1.75 | 33 | 1.17 | 4.61 | +3.83 | 0.9817 | 9714 | 6.51 | FAIL (MCp5) |
| BK.7 | BTC 2024-H2 | 1.75 | 20 | 1.13 | 2.43 | +1.52 | 0.9881 | 9863 | 3.13 | FAIL (trades, MCp5) |
| BK.8 | SOL 2024-H2 | 1.75 | 51 | 2.18 | 3.60 | +6.95 | 0.9766 | 10108 | 4.97 | **PASS** |

**BK: 3/8 PASS**. Todos em ETH 2024-H1 lo e SOL lo/hi. ETH 2025-H1 e BTC falham ambos os lados.

### Série BN (window ±~17% do baseline 30)

| Tag | Combo | w | trd | Sh | MDD% | PnL% | cost_r | MCp5 | MCmdd95% | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| BN.1 | ETH 2024-H1 | 25 | 43 | -0.07 | 4.33 | -0.30 | 0.9797 | 9602 | 5.75 | FAIL (Sharpe, PnL, MCp5) |
| BN.2 | ETH 2025-H1 | 25 | 53 | 0.78 | 4.26 | +2.48 | 0.9727 | 9601 | 6.89 | FAIL (Sharpe, MCp5) |
| BN.3 | BTC 2024-H2 | 25 | 28 | 2.81 | 1.26 | +3.91 | 0.9848 | 10234 | 0.93 | FAIL (trades) |
| BN.4 | SOL 2024-H2 | 25 | 67 | 1.71 | 3.96 | +5.52 | 0.9698 | 10059 | 4.54 | **PASS** |
| BN.5 | ETH 2024-H1 | 35 | 31 | 1.44 | 2.32 | +3.67 | 0.9851 | 10014 | 3.13 | **PASS** |
| BN.6 | ETH 2025-H1 | 35 | 34 | 1.76 | 3.38 | +5.34 | 0.9820 | 9917 | 5.11 | FAIL (MCp5) |
| BN.7 | BTC 2024-H2 | 35 | 18 | 1.88 | 1.92 | +2.33 | 0.9897 | 9995 | 1.59 | FAIL (trades, MCp5) |
| BN.8 | SOL 2024-H2 | 35 | 42 | 1.90 | 3.57 | +6.02 | 0.9797 | 10235 | 2.98 | **PASS** |

**BN: 3/8 PASS**. ETH 2024-H1 hi, SOL lo/hi. ETH 2025-H1 falha ambos. BTC volume insuficiente em w=25 e w=35.

### Série BO (min_width_bps ±20% do baseline 250)

| Tag | Combo | bw | trd | Sh | MDD% | PnL% | cost_r | MCp5 | MCmdd95% | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| BO.1 | ETH 2024-H1 | 200 | 39 | 0.10 | 4.98 | +0.18 | 0.9802 | 9516 | 7.20 | FAIL (Sharpe, MCp5) |
| BO.2 | ETH 2025-H1 | 200 | 41 | 1.43 | 4.69 | +4.67 | 0.9774 | 9686 | 6.81 | FAIL (MCp5) |
| BO.3 | BTC 2024-H2 | 200 | 34 | 2.39 | 1.91 | +3.88 | 0.9815 | 10198 | 1.65 | **PASS** |
| BO.4 | SOL 2024-H2 | 200 | 61 | 1.90 | 3.63 | +6.50 | 0.9722 | 10047 | 5.26 | **PASS** |
| BO.5 | ETH 2024-H1 | 300 | 27 | 3.57 | 1.51 | +8.00 | 0.9871 | 10526 | 1.11 | FAIL (trades) |
| BO.6 | ETH 2025-H1 | 300 | 33 | 1.74 | 3.88 | +5.28 | 0.9826 | 9951 | 4.63 | FAIL (MCp5) |
| BO.7 | BTC 2024-H2 | 300 | 13 | 0.86 | 1.90 | +0.97 | 0.9924 | 9879 | 1.95 | FAIL (trades, Sharpe, MCp5) |
| BO.8 | SOL 2024-H2 | 300 | 50 | 2.75 | 3.47 | +8.35 | 0.9773 | 10335 | 3.61 | **PASS** |

**BO: 3/8 PASS**. BTC lo, SOL lo/hi. ETH 2024-H1 e ETH 2025-H1 falham ambos (ETH 2024-H1 hi falha por trades=27<30 apesar de Sharpe 3.57 — lado "bom" do gate derrotado por volume).

## Classificação por combo × eixo

| Combo | num_std lo/hi | num_std class | window lo/hi | window class | min_width lo/hi | min_width class |
|---|---|---|---|---|---|---|
| ETH 2024-H1 | ✅/❌ | fragile_high | ❌/✅ | fragile_low | ❌/❌ | fragile_both |
| ETH 2025-H1 | ❌/❌ | fragile_both | ❌/❌ | fragile_both | ❌/❌ | fragile_both |
| BTC 2024-H2 | ❌/❌ | fragile_both | ❌/❌ | fragile_both | ✅/❌ | fragile_high |
| SOL 2024-H2 | ✅/✅ | **robust** | ✅/✅ | **robust** | ✅/❌ | fragile_high |

## Classificação 3D consolidada

| Combo | Classe 3D (params corretos) | Classe 3D (ADR-0035, errada) | Delta |
|---|---|---|---|
| ETH 2024-H1 | fragile_3d | fragile_3d_totalmente_fragil | ≈ igual |
| ETH 2025-H1 | **fragile_3d** (3 eixos) | semi_robust_num_std | **PIOR** |
| BTC 2024-H2 | fragile_3d | fragile_3d | igual |
| SOL 2024-H2 | **semi_robust_2d** (num_std + window robustos) | semi_robust_window | **MELHOR** |

## Decisões

### 1. SOL 2024-H2 sobe de `semi_robust_window` → `semi_robust_2d`

SOL é robust em 2 de 3 eixos (num_std + window), frágil apenas em min_width (lado hi). Isto torna SOL 2024-H2 o **único combo com >1 eixo robusto** no manifest. Reforça a escolha de SOL como 1ª onda do rollout.

### 2. ETH 2025-H1 cai de `semi_robust_num_std` → `fragile_3d` completo

A "robustez num_std" do ADR-0033 era artefato do regime errado. Com regime correto, ETH 2025-H1 falha ambos os lados de **todos os 3 eixos** — mais frágil que o próprio ETH 2024-H1 em alguma dimensão (ETH 2024-H1 pelo menos tem num_std=lo e window=hi passando).

**Implicação:** ETH 2025-H1 era considerado "menos arriscado" que ETH 2024-H1; agora é o oposto. Mas **ambos são fragile_3d** — e como `weakest_wins` agrega por (symbol, engine), o live class de ETHUSDT_1h continua `fragile_3d` (antes era `fragile_2d`).

### 3. BTC 2024-H2 permanece `fragile_3d` (estável entre os dois runs)

3 confirmações consistentes. BTC é estruturalmente marginal para esta estratégia. Sugestão ADR-0035 "elevar 2ª onda 14d → 21d paper limpo" mantida, agora com fundamento empírico re-validado.

### 4. Novo `weakest_wins` por (symbol, engine)

| (symbol, engine) | Classe live nova | Classe live antiga (ADR-0034) |
|---|---|---|
| ETHUSDT_1h | fragile_3d | fragile_2d |
| SOLUSDT_1h | semi_robust_2d | semi_robust_window |
| BTCUSDT_1h | fragile_3d | fragile_2d |

**Impacto operacional:**
- ETHUSDT fica **mais conservador** que antes. Em caso de qualquer sinal ruim em live, deve ser suspenso antes de SOL.
- SOLUSDT **ganha** em hierarquia de confiança. Possível candidato a elevação de notional se paper der trades clean (fora de escopo agora; sem pressa para live).
- BTCUSDT permanece em 2ª onda 21d-conservative.

### 5. Manifest v2 atualizado

`robustness.*_sensitivity` e `cross_axis_3d` nos approved_combos substituídos. Flag `robustness_invalidated_by` removida (substituída por `robustness_re_derived_by: "ADR-0038"`).

`rollout_priority_live` atualizado com classes novas.

### 6. ADR-0034 (weakest-wins) permanece válido

A regra não muda. Só mudam os inputs (classes por combo) e, portanto, o output (classes por symbol-engine). Errata do ADR-0034 cabível, mas simples — a estrutura matemática sobrevive.

### 7. Paper-mock: cessação (a/b/c) inalterada

Este ADR é re-derivação epistêmica, não evento runtime. Não conta como critério (b) paragem. `bollinger_width_regime` segue ativo em ETH+SOL. BTC deferred.

### 8. Não reabrir outras séries

A sugestão do ADR-0035 de "Série BP (2-axis interaction)" fica indefinidamente deferred. Prioridade real: (a) ver trades live em paper, (b) Cat B quando datasets/strategies chegarem, (c) port de strategies novas.

## Consequences

**Prós:**
- Números agora correspondem ao manifest executado em produção. Classificações informativas válidas.
- SOL emerge como mais robusto do que supúnhamos → confiança em 1ª onda aumenta marginalmente.
- Paper-mock provou utilidade imediata: detectou bug AF antes de qualquer decisão sub-ótima baseada em classificações erradas.

**Contras:**
- 9/24 pilotos passam (vs 10/24 antes). Config v2 é **mais** estreito do que parecia, não menos.
- ETH 2025-H1 perdeu 100% de qualquer classificação positiva — reduz folga narrativa do deploy.
- Duas ADRs foram publicadas com números errados (0032, 0033, 0035). Erosão pequena de confiança no processo — compensada pela auto-correção transparente via ADR-0037 + ADR-0038.

**Riscos residuais:**
- Com ETHUSDT agora fragile_3d, se aparecer **um** sinal anômalo em live, pode-se argumentar que deveríamos ter suspendido ETH mais cedo. Aceito: mantemos via @botbinance observação ativa.
- O padrão "copiei pattern CLI sem checar manifest" pode ter gerado outros bugs latentes em séries anteriores (AK, AZ). Não há motivo forte pra re-auditar retroativamente se esses runs não informam decisão atual — **mas** se qualquer série futura for iniciada, checklist obrigatório: verificar `engine.params.*` antes de rodar.

## Follow-ups

- [x] Summary scripts: `exports/diag/{bk,bn,bo}_rerun_summary.json`.
- [x] ADR publicado.
- [ ] Atualizar `exports/approved/bollinger_width_regime_20260418_v2.json`:
  - Remover `robustness_invalidated_by` e `robustness_invalidated_reason`.
  - Adicionar `robustness_re_derived_by: "ADR-0038"` + `re_derived_at: "2026-04-19T..."`.
  - Atualizar `robustness.*_sensitivity` e `robustness.cross_axis_3d` em cada combo com valores desta ADR.
  - Atualizar `rollout_priority_live.*.class` com novos weakest-wins.
- [ ] Errata nos ADRs 0032/0033/0035: uma seção "Invalidated by ADR-0037; re-derivado em ADR-0038" no topo. Manter texto original pra auditoria.
- [ ] Reportar @botbinance via bridge: novas classes + impacto (ETH conservador, SOL marginalmente melhor, BTC estável).
- [ ] Checklist novo no protocolo de séries: antes de `alpha-forge validate --regime-filter ...`, re-ler `engine.params.regime_filter` do manifest alvo.

## Artefatos

- Raw reruns: `results/validation/{bk,bn,bo}-rerun-*` (24 dirs).
- Summary scripts: `exports/diag/{bk,bn,bo}_rerun_summary.json`.
- Script extrator: `tools/summarize_reruns.py`.
- Scripts rerun: `tools/run_{bk,bn,bo}_rerun.py`.
- ADR predecessor (bug): `decisions/0037-incident-20260419-regime-filter-params-bug-bk-bn-bo.md`.
- Manifest atualizado: `exports/approved/bollinger_width_regime_20260418_v2.json`.
