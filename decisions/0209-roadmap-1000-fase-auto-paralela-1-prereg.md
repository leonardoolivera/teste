# 0209 — Roadmap 1000 Fase Auto-Paralela 1 (no-filter wave) — pre-reg

**Status:** Proposed (pre-reg)
**Date:** 2026-04-25
**Deciders:** Usuário ("vamo fazer tudo... rodar varios simultaneamente"), agente
**Relates to:** ADR-0203 (roadmap 1000), ADR-0202 (TF10m exauridamente refutado)

## Context

ADR-0203 estruturou roadmap de 1000 probes em 4 tiers, com diretiva de execução por **Fase** (20-30 probes) com pre-reg + check-in. Até agora, 50 probes executados (MA01, MA02, ST01, BT01, AE01) cobrindo apenas 5 batches manuais de Tier 1 TF10m. O usuário pediu execução agressiva (paralelizar tudo que o hardware aguentar).

Hardware disponível: AMD Ryzen 5 5600GT (6 cores / 12 threads), 16 GB RAM. Smoke test de 1 probe MA crossover 10m custou 5.9s wall-clock — muito abaixo do orçamento original de 10min/probe assumido em ADR-0203 (datasets pequenos + estratégias rápidas).

## Decision

Construir dispatcher paralelo único (`tools/run_roadmap_auto.py`, ProcessPoolExecutor=10) que consome `roadmap_1000.json` e dispara automaticamente todos os entries imediatamente runnable, em waves filtradas por `regime_filter`. **Fase 1 (este ADR)**: wave `regime_filter='none'`, 204 probes (engines `bollinger`, `rsi`, `ma_crossover`, `supertrend`, `composite_bb_rsi`, `keltner`, `zscore` — engines suportados pela CLI; params concretos). Estimativa wall-clock 5-15min.

Resumable via `exports/diag/roadmap_auto_progress.json`. Métricas computadas inline (Sharpe anualizado TF-aware, trades, PnL%, MDD%, final equity).

## Consequences

- **Positive:** cobertura sistemática rápida de Tier 1 + Tier 2 sem filtro de regime (baseline para benchmark de filter contribution); identificação automática de probes que cruzam gate Sh ≥ 1.5 ∧ trades ≥ 30; saturação de hardware (~83% de logical cores).
- **Negative:** redo parcial de probes já executados em batches MA01/MA02/ST01/BT01/AE01 (~30 entries de overlap, ~3min de compute redundante — aceitável); MC e cost stress mantidos no nível default da CLI (mc-resamples=500), não alongados.
- **Neutral:** entries com filtro `width_basic` (180), `stack_canonical` (24) ficam para Fase Auto-Paralela 2 após mapear translator dos filtros para CLI. Entries `canonical` (232) e perturbações relativas (30) ficam para Fase 3 após definir baselines. Engines `regime_meta`, `portfolio_*`, `stack_combo`, `exotic_*`, `ml_*` (310 probes) requerem código novo — Fase final.

## Update 2026-04-25 (durante Fase 1)

Enquanto Wave 1 rodava, foram implementados em `tools/run_roadmap_auto.py`:

1. **Filter translator** (`width_basic`, `stack_canonical`, `width:min=N`, `trend_htf:4h:sma=N:mode`, `AND(...)`, `OR(...)`) → CLI `--regime-filter SPEC`. Filtros não-mapeáveis (atr_expansion_50pct, trend_htf_4h_sma50_flat, realized_vol_percentile_70, width_narrow_10m, funding_rate_extreme, ablation_*) flagged como `__UNSUPPORTED__` — requerem regime_meta engine novo.
2. **Canonical defaults table** (`CANONICAL_DEFAULTS` por engine, ADR-0028+0011+0008 baselines): bollinger=20/2.0, rsi=14/30/70, ma_crossover=20/50, supertrend=10/3.0, composite_bb_rsi=20/2.0/30/70, keltner=20/14/2.5, zscore=20/2.5, donchian=20/10.
3. **Engine donchian** adicionado a `SUPPORTED_ENGINES` (faltava no v1 do dispatcher).
4. CLI flags `--filter-set with_filter` e `--filter-set all` para waves seguintes.

Total runnable expandido: **204 → 576 candidatos** (57.6% do roadmap atingível sem código novo).
Restante: ~30 perturbações relativas (resolver `num_std += 0.25` contra baseline canonical) + ~394 que precisam código (regime_meta, portfolio_*, stack_combo, exotic_*, ml_*, ablation_*, filtros raros).

## Critério de aprovação por engine (gate agregado)

Por engine no wave, contar probes com `sharpe ≥ 1.5 AND trades ≥ 30`:
- ≥ 30% de probes passando gate em pelo menos 2 assets distintos → engine entra para análise cross-era + pre-reg de validação OOS dedicada.
- < 30% → engine refutado nesta wave; closeout note no ADR de fechamento.

Gate alfa (PnL real > B&H/leverage) aplicado em pós-análise via summarizer com `BH_APPROX` table.

## Stop conditions

- Erros de subprocess > 5% → pausar e investigar.
- Probes com timeout 30min (default) → marcar como falhados, seguir.
- User redirect → obedecer.

## Alternatives considered

- **Manual: definir 4 batches BB01/RS01/DC01/CB01 (40 probes)** — rejeitado: subutiliza hardware (4 paralelos manuais quando dá pra rodar 10) e força N rodadas para esgotar.
- **Pool de 6 (físicos apenas)** — rejeitado: smoke test mostrou processos CLI são leves; SMT extra dá throughput sem thrashing.
- **Pool de 12 (todos lógicos)** — rejeitado: zero margem para I/O do dispatcher e OS.

## Follow-ups

- Disparar dispatcher em background, capturar log em `exports/diag/roadmap_auto_phase1.log`.
- Após completar: gerar `roadmap_auto_phase1_summary.json` com gate sh/alfa por probe agrupado por engine.
- Closeout ADR consolidando achados por engine e demarcando próxima Fase (filter translator).
