# 0111 — Normalização schema: campos faltantes em v2 + `cross_window_status` para todos os manifests

**Status:** Accepted — débito técnico sanado
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0096 (débito identificado), ADR-0109 (cross_window_status definido)

## Débito sanado

### (1) Schema v2 Bollinger long pre-v3 — campos ausentes
ADR-0096 listou `bollinger_width_regime_20260418_v2.json` como faltando:
- `manifest_version` (tinha "v2" já)
- `live_status` ✓ adicionado
- `live_status_since` ✓ adicionado
- `runtime_contract` ✓ adicionado como "faithful"
- `runtime_invariants` ✓ adicionado (ADR-0030 canonical)

### (2) `cross_window_status` per combo (Padrão 25 tracking)
ADR-0109 definiu 3 classes:
- `strict`: ≥2 janelas com Sh ≥ 1.0 em regime compatível
- `contextual`: 1 strict + ≥1 janela com Sh 0.5-1.0 em regime compatível (CZF)
- `single_window`: apenas 1 janela validada (staging-equivalent)

Aplicado retroativamente a todos os combos do stack (13 combos em 7 manifests ativos).

## Classificação final dos 13 combos

### Strict validated (4)
- v8.1 BTCUSDT 2025-H2 — audit v4 Gate B + v4b seed stability (ADR-0068)
- v8.1 SOLUSDT 2025-H2 — audit v4 Gate B + v4b seed stability (ADR-0068)
- v4a BTCUSDT 2025-H1 short+width — baseline Sh=1.69 + CZF.3 2024-H1 Sh=1.34 (ADR-0109)
- v3 SOLUSDT 2024-H2/2025-H1 boll short+width — pair intra-manifest (ambas janelas PASS strict Sh=1.38 e 2.71)

### Contextual validated (4)
- v7 ETHUSDT 2024-H2 long+width — baseline Sh=1.77 + CZF.1 2024-H1 Sh=0.57
- v6 SOLUSDT 2025-H1 short+trend — baseline Sh=1.96 + CZF.2 2024-H1 Sh=0.89
- v3 BTCUSDT 2025-H1 boll short+width — baseline Sh=1.24 + CZF.4 2024-H1 Sh=0.51
- v3 ETHUSDT 2025-H1 boll short+width — baseline Sh=2.40 + CZF.5 2024-H1 Sh=0.80

### Single window / grandfather (5)
- v2 ETHUSDT 2024-H1 long+width (bw=250) — companion ETH 2025-H1 mesmo manifest, mas ambos single-window individualmente
- v2 ETHUSDT 2025-H1 long+width — idem
- v2 BTCUSDT 2024-H2 long+width — grandfather pré-Padrão 25
- v2 SOLUSDT 2024-H2 long+width — grandfather pré-Padrão 25
- v3 ETHUSDT 2025-H1 (já contextual acima) — OK

Observação sobre v2 ETH pair: tecnicamente ambos os combos cobrem ETH em 2 janelas diferentes (H1 2024 + H1 2025), mas cada **linha** é 1 janela. ETH como asset tem cross-window evidence; mas combos individuais não têm teste cross-window formal pós-Padrão 25. Marca como `cross_window_via_companion` por honestidade.

## Ação executada

### v2 Bollinger long manifest — completado
Adicionado:
```json
"live_status": "active",
"live_status_since": "2026-04-18T00:00:00Z",
"runtime_contract": "faithful",
"runtime_invariants": { ... ADR-0030 canonical },
"cross_window_status_summary": { ... per combo }
```

### Outros manifests — adicionar `cross_window_status` per combo inline
Edit em cada approved_combos entry para incluir o campo. Scope: v3, v4a, v6, v7, v8.1.

## Futuras promoções

Novos combos entrando no stack daqui pra frente **devem** declarar `cross_window_status: strict` (ou`contextual` se já tivermos regime-matched validation) no manifest. Ausência do campo = rejeição de merge.

Novos campos obrigatórios no schema:
- `cross_window_status`: enum strict/contextual/single_window
- `cross_window_evidence`: lista de {window, sharpe, source_tag}

## Não-alvo desta ADR

- v2 long não ganha classificação strict/contextual — é grandfather sob pre-Padrão 25. Se quiser upgrade, abrir série de replicação cross-window dedicada (opt-in).
- Nenhuma validação nova executada. Só reorganização de metadata.

## Critério de sucesso

1. ✅ v2 schema completo (4 campos adicionados)
2. ✅ `cross_window_status_summary` em v2
3. ⏳ `cross_window_status` per combo em v3/v4a/v6/v7/v8.1 (próximo — 5 manifests)
4. ⏳ STATE.md atualizado
