# 0140 — Manifest v6.1: RSI trendhtf SOL 2025-H1 bounds 25/75 promotion

**Status:** Accepted — manifest editado, live_status=active
**Date:** 2026-04-20
**Deciders:** Usuário (autorização "sim") + agente
**Relates to:** ADR-0134 (CZ10), ADR-0135 (CZ10 closeout), ADR-0136 (CZ11), ADR-0137 (CZ11 closeout), ADR-0138 (CZ12), ADR-0139 (CZ12 closeout), Padrão 40

## Contexto

Após Série CZ10 (sensibilidade) + CZ11 (2ª janela) + CZ12 (3ª janela cross-era), o combo **RSI short trend_htf SOL 2025-H1** acumulou 3/3 PASS strict com bounds 25/75:

| Janela | Regime | Sharpe 25/75 | Sharpe 30/70 (canônico) |
|---|---|---:|---:|
| 2025-H1 | chop | 2.00 | 0.89 |
| 2025-H2 | misto | 3.36 | — |
| 2024-H1 | chop | 1.99 | — |

Sharpe médio esperado ≈ 2.45 (vs 0.89 canônico). Gate Padrão 40 (cross-era 2024 + 2025) atendido.

Paralelamente, SOL naked 25/75 foi **refutado** em CZ12 (Sh=-0.07 em 2024-H1), mantém-se 30/70 no manifest v4b — ver ADR-0139.

## Decisão

Promover bounds 25/75 para o combo SOL trend_htf 2025-H1 via edit do manifest existente (não criar novo manifest — mantém supersedes chain limpo).

### Edits aplicados em `exports/approved/rsi_short_trendhtf_2025h1_sol_20260420.json`

1. `manifest_version`: `"v6"` → `"v6.1"`
2. `engine.params.oversold`: `30` → `25`
3. `engine.params.overbought`: `70` → `75`
4. `approved_combos[0].oos_sharpe`: `1.96` → `2.00` (CZ10.5 25/75 baseline)
5. `approved_combos[0].oos_trades`: 34 → 32
6. `approved_combos[0].oos_pnl_pct`: atualizado para 9.80
7. `approved_combos[0].approved_in`: `"v6"` → `"v6.1"`
8. `approved_combos[0].source_tag`: `"CZ10.5 (25/75 baseline 2025-H1)"`
9. `approved_combos[0].source_run_id`: `"cz10-sol-rsi-2575-trendhtf-1h-2025h1"`
10. `approved_combos[0].cross_window_status`: `"contextual"` → `"strict"`
11. `approved_combos[0].cross_window_evidence`: rebuilt com 3 entries (2025-H1/2025-H2/2024-H1)
12. Novo campo `param_upgrade_adr` apontando para este ADR
13. Novo campo `param_upgrade_note` explicando motivação

Demais campos (runtime_invariants, validation, execution_hints, expansion_policy) inalterados — a promoção é apenas bounds, não muda engine/filter/sizing.

### Não alterado

- Outros manifests (v4a, v4b etc) — escopo SOL trendhtf 2025-H1 apenas
- Stack composition (13 combos)
- Bot paper-trade config (bridge post comunicará mudança)

## Raciocínio

### Por que promover agora

3/3 PASS strict cross-era é evidence mais forte que os gates canônicos exigem. Padrão 40 (formalizado em ADR-0139) pede ≥1 janela de 2024 + ≥1 janela de 2025: atendido com 2024-H1 + 2025-H1/H2.

Sharpe lift +1.11 (2.00 vs 0.89) é large effect, não marginal. MC p5 final equity 9712 (vs ~9600 canônico) mantém cauda esquerda aceitável.

### Por que não criar manifest novo

`supersedes` chain existente já expressa lineage. Criar novo arquivo fragmenta busca e quebra convenção "1 combo ativo = 1 manifest live". Edit in-place com bump de versão + ADR referência é mais limpo.

### Por que não promover SOL naked

Refutado em CZ12.1 (Sh=-0.07 2024-H1). Bounds 25/75 era-específico 2025, não generaliza. v4b canônico 30/70 preserva cobertura 2024-H2 + 2025-H2.

## Monitoramento pós-promoção

- Bot deve aplicar oversold=25, overbought=75 no próximo reload do manifest
- Bridge post avisa bot (signal-only): "manifest rsi_short_trendhtf_2025h1_sol bumped v6→v6.1, bounds 30/70→25/75, live imediato"
- Próxima janela 2026-H1 SOL (quando disponível): validar se edge 25/75 persiste em era nova. Se Sh < 1.0, reabrir discussão rollback.

## Aplicação Padrão 40 (cross-era upgrade)

Primeira aplicação prospectiva: qualquer futuro upgrade de params em combos live seguirá o mesmo gate (≥1 janela 2024 + ≥1 janela 2025, Sh ≥ 1.0 em cada).

## Ação executada

- ✅ Manifest editado (13 edits)
- ✅ ADR-0140 escrito
- ⏳ STATE.md tarde-5 entry
- ⏳ Bridge post para bot

## Não-alvo

- Não promover SOL naked 25/75 (refutado)
- Não tocar outros manifests
- Não mudar stack composition
- Não iniciar canary/live — já está active, apenas params mudaram
