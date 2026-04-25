# AUDIT.md — H.7 Donchian 10/5 BTC 180d

release_decision: fail

## release_decision

**`fail`** por dupla violação: critério 1 (`hit_rate=31.77% < 45%`) + critério 3 (`spread+10/baseline=0.9196 < 0.95`).

## Blockers

Nenhum blocker operacional. Pipeline limpo; validador verde.

## Findings

1. **Janela menor não resolve plateau.** Hit_rate=31.77% é o maior de qualquer piloto BTC 180d até agora, mas ainda longe de 45%. Plateau é **parcialmente** hiperparâmetro-dependente (sim, melhora ~2 pp em relação a 20/10) mas não cruza o critério.
2. **Critério 3 quebra.** Janela menor = 74% mais trades (192 vs 110 H.1) = custos dominam em stress (Δ spread+10 = −8.04%). Primeira vez que uma variação de janela quebra o critério de robustez a custos.
3. **p95 MC cruza 10000 pela primeira vez** no protocolo com BTC (10116.28) — cauda superior existe, mas mediana e cauda inferior continuam sub-breakeven.

## Recomendações

- Janela muito curta é sub-ótima para BTC 180d — custos dominam edge.
- Próximo experimento (H.8) testa direção oposta: Donchian 40/20 — se janela maior reduzir custos sem perder edge, define zona operacional razoável.

---

## Re-auditoria 2026-04-18 (ADR-0025)

release_decision: paper_only

**Critério vigente:** híbrido (ADR-0025) — `canary_only` exige `hit_rate ≥ 45%` absoluto; `paper_only` exige top-3 por `composite_score` (ADR-0024) com N ≥ 9.

**Snapshot de ranking (2026-04-18, DEFAULT_WEIGHTS de ADR-0024):**

- Rank: **2/12**
- `composite_score`: **6.87**
- `hit_baseline`: **31.77%** (< piso de 45%)
- `fe_baseline`: **9532.45**
- `flags_digest`: `30b893e48e87736a`

**Justificativa:** top-3 por `composite_score` (ADR-0024) em sample N=12 ≥ 9 → canal relativo `paper_only` habilitado (ADR-0025).

**Decisão original preservada acima.** Esta seção é append imutável; revogações futuras devem ser **nova seção**, nunca edit.
