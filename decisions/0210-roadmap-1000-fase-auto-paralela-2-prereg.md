# 0210 — Roadmap 1000 Fase Auto-Paralela 2 (with_filter + canonical) — pre-reg

**Status:** Proposed (pre-reg)
**Date:** 2026-04-25
**Deciders:** Usuário ("vamo fazer tudo paralelo"), agente
**Relates to:** ADR-0209 (Fase 1), ADR-0203 (roadmap 1000)

## Context

Após Fase 1 (Wave no-filter, 204 probes) executada com 10 workers paralelos, expandimos o dispatcher (`tools/run_roadmap_auto.py`) com:

- Filter translator (width_basic, stack_canonical, width:min=N, trend_htf, AND/OR).
- Canonical defaults table por engine.
- Donchian engine.

Expandido total runnable de 204 → 576. Wave 2 cobre os 372 probes adicionais (filter + canonical + donchian).

## Decision

Disparar Wave 2 = `--filter-set all` (cobre tanto `none` quanto `with_filter`, deduplicado contra `roadmap_auto_progress.json`). Mesmo pool=10. Estimativa: ~2-5min wall-clock pros 372 todo (paralelismo já validado em Wave 1).

## Critério de aprovação por engine (gate agregado)

Idêntico a ADR-0209: por engine, contar probes com `sharpe ≥ 1.5 AND trades ≥ 30`. ≥30% pass-rate em ≥2 assets distintos → engine entra em validação OOS dedicada. Filtro stack_canonical (canonical reference) merece análise separada — provável melhor pass-rate vs no-filter (validação da hipótese "stack v2 filter helps").

## Stop conditions

Idêntico a Fase 1.

## Follow-ups

- Após Wave 2 completar, summarizer agregado cobre Fase 1+2 (data: `roadmap_auto_progress.json`).
- ADR de closeout consolidado (Fase 1+2) com pass-rate cross-filter, identificando engines/configs candidatas a OOS dedicada.
- Fase 3 (próximo): mapear perturbações relativas (`num_std += 0.25`) → ~30 probes adicionais.
- Fase Final: implementar engines novos (regime_meta, portfolio_stack13, stack_combo) — requer dev real.
