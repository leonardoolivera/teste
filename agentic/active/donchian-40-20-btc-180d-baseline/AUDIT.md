# AUDIT.md — H.8 Donchian 40/20 BTC 180d

release_decision: fail

## release_decision

**`fail`** por critério 1 (`hit_rate=24.49% < 45%`).

## Blockers

Nenhum. Pipeline limpo. Critérios 2, 3 e corroboração auxiliar passam com folga.

## Findings

1. **Janela maior reduz custos drasticamente mas não melhora hit.** Trade_count=49 (−55% vs H.1 110); spread+10 Δ=−2.04% (melhor do protocolo). Hit=24.49% (pior que H.1 25.45%).
2. **Zona operacional de robustez a custos existe.** Se algum futuro pipeline tiver edge ≥45% (via outra família ou HMM), janela ≥40 provavelmente protege contra custos melhor que 20/10.
3. **Dois folds > 10000 (fold 1 H.7 + fold 1 H.8)** — tail superior é persistente com janelas diferentes.
4. **Fold 3 colapsou (hit 8.33%)** — janela maior + poucos trades = distribuição de hit muito dispersa entre folds.

## Recomendações

- Janela é trade-off: menor = mais trades + custos dominam (H.7); maior = poucos trades + alta variância fold-a-fold (H.8). **Zona 20/10 parece ser compromisso razoável**, mas nenhuma janela cruza 45%.
- Plateau de hit é **robusto contra variação de janela** — evidência adicional de que é estrutural ao dataset/estratégia, não hiperparâmetro.

---

## Re-auditoria 2026-04-18 (ADR-0025)

release_decision: fail

**Critério vigente:** híbrido (ADR-0025) — `canary_only` exige `hit_rate ≥ 45%` absoluto; `paper_only` exige top-3 por `composite_score` (ADR-0024) com N ≥ 9.

**Snapshot de ranking (2026-04-18, DEFAULT_WEIGHTS de ADR-0024):**

- Rank: **9/12**
- `composite_score`: **4.65**
- `hit_baseline`: **24.49%** (< piso de 45%)
- `fe_baseline`: **9528.27**
- `flags_digest`: `01e6827e6f7cc77b`

**Justificativa:** rank 9/12 por `composite_score`; fora do top-3 → permanece `fail` sob ADR-0025. `hit_rate`=24.49% < 45% também impede `canary_only`.

**Decisão original preservada acima.** Esta seção é append imutável; revogações futuras devem ser **nova seção**, nunca edit.
