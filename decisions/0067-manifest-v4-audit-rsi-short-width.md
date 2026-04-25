# ADR-0067 — Audit pré-registrado manifest v4 (RSI short + width 300)

- **Data:** 2026-04-19
- **Status:** Aceita — pré-registro antes de rodar
- **Relacionadas:** ADR-0059 (audit manifest v3, template), ADR-0065 (promoção v4), ADR-0066 (schema adenda)

## Contexto

ADR-0065 propôs manifest v4 `rsi_short_width_20260419.json` com 4 combos aprovados (CH.4 BTC 2025-H1, CH.6 SOL 2025-H1, CH.7 BTC 2025-H2, CH.9 SOL 2025-H2). Manifest está em `live_status: pending_audit`; ativação exige PASS neste audit.

Template é ADR-0059 (audit v3 CG). Três gates pré-registrados antes de rodar — se qualquer falhar, manifest v4 não ativa sem ADR modificadora.

## Audit pré-registrado

### Gate A — Seed stability (lucky-MC check)

**Procedimento:** re-rodar os 4 combos aprovados com seeds MC {1337, 2024} (seed 42 já arquivado). Total: 8 runs.

**Critério PASS:** manifest gate (trades≥30, Sharpe≥1.0, MDD≤20, MC p5>9500, cost_r≥0.95) continua PASS nos 3 seeds × 4 combos = **12/12**. Se ≤1 combo falhar em 1 seed isolado, ainda conta como PASS (1 FAIL é ruído aceitável dado MC stochastic). Se ≥2 combos falharem em qualquer seed, Gate A FAIL.

### Gate B — Filter load-bearing (atribuição)

**Procedimento:** re-rodar os 4 combos sem `--regime-filter` (RSI puro sem width 300). 4 runs.

**Critério PASS:** **≥3/4 combos** mostram manifest gate FAIL sem filter. Confirma que filter é load-bearing, não cosmético. Se **4/4 ainda passarem sem filter**, manifest é refutado — filter não é necessário e escopo v4 deve colapsar pra "RSI short puro" (manifest separado, nova ADR).

### Gate C — Exclusion confirmation (scope creep check)

**Procedimento:** re-rodar os 2 piores combos excluídos (CH.1 BTC 2024-H2 Sh=−0.76 e CH.5 ETH 2025-H1 Sh=0.50) com seed 1337 + filter ativo. 2 runs.

**Critério PASS:** ambos continuam **FAIL no manifest gate**. Se algum virar PASS no seed 1337, exclusão vira incorreta e escopo precisa expandir — blocker pra ativação.

### Total: 14 runs (~25 min)

8 (A seeds 1337+2024) + 4 (B no filter) + 2 (C exclusion) = 14 runs novas.

## Scripts

- `tools/run_manifest_v4_audit.py` — executa 14 runs.
- `tools/summarize_manifest_v4_audit.py` — agrega e emite verdict por gate.

## Escopo fora

- Re-rodar seed 42 dos 4 aprovados (já em `results/validation/ch-rsi-*-short/`).
- Audit B com filter modificado (width 250 ou 350) — fora do escopo v4, seria nova série.
- Audit de CH.2/CH.3/CH.8 (outros excluídos) — CH.1 e CH.5 são os casos limítrofes; CH.2/3/8 são FAIL por margem maior e não representam scope creep risk.

## Critério de sucesso desta ADR

1. Gates A/B/C executados na ordem ✓
2. Verdict pré-registrado documentado ADR-0068 closeout
3. Se PASS 3/3: ADR-0068 ativa manifest v4 + notifica bot
4. Se FAIL qualquer gate: ADR-0068 documenta razão + decide retreat (manifest v4 não ativa)
