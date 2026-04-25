# 0139 — Série CZ12 closeout: SOL naked 25/75 refutado, SOL trendhtf 25/75 3/3 strict

**Status:** Accepted — 1 promoção técnica autorizada (SOL trendhtf), 1 rollback candidato (SOL naked)
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0138 (pré-reg), ADR-0137 (CZ11), Padrões 25/38/39

## Resultado 3ª janela

| Tag | Combo | Janela | Tr | Sh | PnL% | MDD% |
|---|---|---|---:|---:|---:|---:|
| CZ12.1 | SOL naked 25/75 | 2024-H1 chop | 50 | **-0.07** | -1.29 | 14.21 |
| CZ12.2 | SOL trendhtf 25/75 | 2024-H1 chop | 30 | **1.99** | +8.64 | 5.69 |

## Consolidação final cross-window (CZ10 + CZ11 + CZ12)

### SOL naked 25/75 — REFUTADO

| Janela | Regime | Sh |
|---|---|---:|
| 2025-H2 | misto | 3.61 ✅ |
| 2025-H1 | chop | 1.52 ✅ |
| 2024-H1 | chop | **-0.07** ❌ |
| 2024-H2 | bull | -1.71 (Padrão 26) |

Gate ADR-0138: "CZ12 Sh < 0.3 → refutação upgrade, manter 30/70". **Atingido (-0.07).** CZ10 + CZ11 PASS era padrão era-2025-específico. 2024-H1 (chop pré-bull) quebrou o edge 25/75, enquanto 30/70 canônico v8.1 não foi testado em 2024-H1 (gap de evidence).

Decisão: **manter SOL naked 30/70 no manifest.** Rollback do candidato upgrade. Registrar padrão de era-dependência.

### SOL trendhtf 25/75 — PROMOÇÃO TÉCNICA CONFIRMADA

| Janela | Regime | Sh |
|---|---|---:|
| 2025-H1 | chop | 2.00 ✅ |
| 2025-H2 | misto | 3.36 ✅ |
| 2024-H1 | chop | **1.99** ✅ |
| 2024-H2 | bull | -0.19 (filter contém) |

**3/3 regime-compatível PASS strict** (todos Sh ≥ 1.99). Baseline canônico 30/70 era 0.89; upgrade 25/75 mostra 2.00+ consistente em 3 eras diferentes. Filter trend_htf short_only + bounds extreme é combinação robusta.

Gate ADR-0138: "3/3 regime-compatível Sh ≥ 1.0 → atualizar manifest". **Atingido com folga.**

## Padrão 40 (NOVO): era-dependence pode invalidar cross-window mesmo com Padrão 25 atendido em 2/3

2/3 PASS strict (CZ11) parecia suficiente pro gate Padrão 25 original. Adicionar 3ª janela de **era diferente** (2024-H1 vs 2025) pode revelar era-dependência que não aparece em janelas da mesma era.

Implicação: para upgrades de params (não combo novo), exigir cross-era além de cross-window. Combo canônico (30/70) já validado cross-era; variante (25/75) precisa de evidence cross-era equivalente antes de promoção.

Aplicação imediata: SOL naked 25/75 refutado por Padrão 40. Regra prospectiva: upgrades de params em combos live requerem **≥1 janela em cada uma de 2 eras** (2024-H1/H2 + 2025-H1/H2 = 4 janelas-ano disponíveis; exigir 1 de 2024 + 1 de 2025 mínimo).

## Decisão produção (atualizada)

**Autorização pendente do usuário (escopo reduzido):**
- SOL trendhtf 25/75: gate atendido, aguardando autorização explícita pra editar manifest + ADR promoção + bridge post
- SOL naked: REFUTADO, não promover, manter 30/70 canônico

Se autorizado, ação sobre o manifest:
- `exports/approved/rsi_short_trendhtf_2025h1_sol_20260420.json`: atualizar rsi_oversold=25, rsi_overbought=75
- Adicionar ao manifest campo `param_upgrade_adr: "0139"` ou similar
- Atualizar cross_window_status_summary com 3/3 evidence
- Manter Sharpe expected = média das 3 janelas ≈ 2.45 (vs 0.89 canônico)

## Ação executada

- ✅ ADR-0139 closeout
- ✅ Série CZ12 documentada
- ✅ STATE.md entry (tarde-4)
- ⏳ Decisão produção pendente sobre SOL trendhtf 25/75

## Não-alvo

- Não promover SOL naked 25/75 (refutado Padrão 40)
- Não editar manifest sem autorização
- Não alterar stack composition

## Stack pós-CZ12

13 combos inalterados. Achado consolidado: **1 combo (SOL trendhtf) pendente upgrade 30/70 → 25/75**, Sharpe esperado ~2.45 vs 0.89 canônico.
