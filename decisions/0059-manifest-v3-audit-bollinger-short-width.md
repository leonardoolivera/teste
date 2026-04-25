# 0059 — Audit do manifest v3 bollinger_short_width_20260419 (pré-registro + execução)

**Status:** Accepted — pré-registro; execução imediata
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0048 (audit manifest v2, template), ADR-0058 (promoção manifest v3), manifest `exports/approved/bollinger_short_width_20260419.json`.

## Context

ADR-0058 gravou manifest v3 com `live_status=pending_audit`. Antes de notificar BotBinance e marcar `active`, três riscos precisam ser fechados — espelho direto de ADR-0048:

1. **Lucky-seed MC**: 4 combos aprovados podem ter saído de seed MC favorável. MC p5 em CG.4 (9953) e CG.5 (9924) estão a ≤50bp do gate 9500 — sensíveis a perturbação.
2. **Filtro decorativo**: `BollingerWidthFilter:min_width_bps=300` pode não estar carregando peso real no short. Hipótese testável: sem filtro, cost_r colapsa.
3. **Exclusões sem reconfirmação**: 5 combos excluídos em `expansion_policy`. CG.1 e CG.9 são os mais severos — reconfirmar que não foi artefato de seed.

Custo: ~14 runs, ~25min. Benefício: se passa, manifest ativa limpo; se falha, captura-se problema antes de bot paper-tradar.

## Método

### Audit A — estabilidade MC (12 runs)

4 combos × 3 seeds (42, 1337, 2024) = 12 runs. Seeds 1337 e 2024 reutilizam os mesmos usados em ADR-0048 (continuidade). Sharpe/fe/MDD devem ser **determinísticos** entre seeds (WF é determinístico); MC p5 pode variar ≤50bp esperado.

**Gate A**: em todos os 4 combos × 3 seeds, gates manifest (trades≥30, Sharpe≥1.0, MDD≤20, MC p5≥9500, cost_r≥0.95) **passam**. 12/12 PASS.

### Audit B — atribuição do filtro (4 runs)

4 combos sem `regime_filter` (Bollinger short 20/1.5 puro). Espelho direto de ADR-0048 Audit B, que mostrou filtro load-bearing no long (sem filtro: MC p5 9968 < 9500).

**Gate B**: em pelo menos 3/4 combos, remover filtro quebra pelo menos um gate (cost_r ou MC p5). Se em todos 4 filtro é neutro, hipótese "filtro load-bearing no short" é refutada — manifest não representa corretamente a origem do edge.

### Audit C — exclusão confirmação (2 runs)

CG.1 (BTC 2024-H2, Sharpe 0.52) e CG.9 (SOL 2025-H2, triplo FAIL) com `mc_seed=1337` (diferente do 42 original). Se exclusão se mantém, expansion_policy é robusta.

**Gate C**: CG.1 e CG.9 continuam FAIL pelo menos um gate com seed alternativo. Se passam com seed 1337, exclusão foi artefato — reabrir série.

### Regras anti-movimento

- Gates fixos. Não renegociáveis post-hoc.
- Tooling: `tools/run_manifest_v3_audit.py` + `tools/summarize_manifest_v3_audit.py`.
- Outputs: `results/validation/audit-v3-*`, `exports/diag/manifest_v3_audit_summary.json`.

## Resultado esperado

- **Audit A PASS + B PASS + C PASS** → ADR-0060 marca manifest `live_status=active` e posta em `inbox_botbinance.md`.
- **Qualquer check FAIL** → ADR-0060 documenta falha, reverter promoção (`live_status=blocked`), escolher próxima direção (retreinar série, ajustar gate, arquivar combos individualmente).

## Consequences

**Positive:**
- Audit barato (~25min) vs risco de bot paper-tradar manifest fantasma.
- Template reutilizável (v4+ pode usar mesmo script).

**Negative:**
- Se Audit B falhar (filtro decorativo), ADR-0057 padrão 10 precisa revisão — "filtro parametrizado ao regime" pode ser narrativa post-hoc.
- Se Audit A falhar em CG.4 (37 trades borderline), combo precisa sair do manifest.

**Neutral:**
- Manifest v2 não afetado.
- Bot continua paper-tradando v2 independentemente.

## Critério de sucesso

1. 14 runs sem crash.
2. Summarizer emite `manifest_v3_audit_summary.json` interpretável.
3. ADR-0060 decide `active` vs `blocked` com base nos 3 gates.
