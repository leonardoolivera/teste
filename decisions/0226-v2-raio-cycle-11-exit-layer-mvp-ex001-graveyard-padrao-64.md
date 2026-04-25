# 0226 — V2/RAIO Ciclo 11 — Exit_layer MVP + EX001 GRAVEYARD + Padrão 64 + AGENTS.md guideline

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13
**Relates to:** ADR-0225 (Cycle 10 closeout), ADR-0223 (consolidação Padrões 53-62), ROADMAP_ESTRATEGIAS_V2_METODOLOGICO.md (Top 6 V2)

## Contexto

Cycle 10 fechou a fase de auditoria retroativa V1 (P52, P50, stack 13). Cycle 11 abre nova frente: **implementar exit_layer engine** para destravar família EX (36 hipóteses V2). EX001 (time stop curto melhora MR) é Top 6 V2 por priority_score.

Ciclo 11 contém 3 sub-tarefas:

### Cycle 11.B — Update AGENTS.md com methodology guideline V2

[AGENTS.md §9](../AGENTS.md) adicionado consolidando Padrões 53-63 como **mandatory reading** para qualquer agente trabalhando em strategy approval. Inclui:
- Core gate (9 critérios AND-conjunto pra promoção a manifest).
- Padrões falsificados (P50, P52, P57 — não repetir).
- Reaberturas (TF 10m permanently graveyarded).
- Operational protocols (stack 13 health pós-Padrão 60).
- Pointers pros 6 methodology files (HYPOTHESIS_TREE, NODE_LOG, SEARCH_STATE, GRAVEYARD, ROADMAP_V2, RAIO).

### Cycle 11.A — TimeStopWrapper engine MVP

Implementação:
- [`src/alpha_forge/strategies/exit_layer.py`](../src/alpha_forge/strategies/exit_layer.py) — `TimeStopWrapper` decora qualquer Strategy. Estado mutável por instância (`_bars_in_position`); reset em ENTER / EXIT explícito; força EXIT após N bars.
- CLI flag `--time-stop-bars N` em [`src/alpha_forge/cli/app.py`](../src/alpha_forge/cli/app.py). 0 (default) desativa.
- `_build_strategy` factored em `_build_strategy_base` + wrapping conditional.

Smoke test confirma: bollinger 30/1.5 + filter + time_stop=12 sobre BTC 30m gera 125 trades em 4 folds (vs ~150-200 baseline).

### Cycle 11.C — EX001 Scout

Tools: [`tools/v2_ex001_time_stop_scout.py`](../tools/v2_ex001_time_stop_scout.py). Bollinger canonical (20/2.0 long_only + width filter) com 5 variants (raw, ts06, ts12, ts24, ts48) × 3 assets sobre janela contínua 30m. 15 probes em 23s wall-clock.

**Resultado:**

| Asset | raw | ts06 | ts12 | ts24 | ts48 |
|---|---:|---:|---:|---:|---:|
| BTC Sh | 0.14 | **-1.18** | 0.02 | 0.13 | 0.14 |
| ETH Sh | 0.15 | -0.49 | -0.04 | 0.15 | 0.15 |
| SOL Sh | -0.21 | -0.07 | **+0.15** | -0.14 | -0.21 |

**Pass count Padrão 60 (Sh ≥ 1.0 ∧ tr ≥ 30 ∧ MDD ≤ 10%): 0/15.**

Observações:
1. **ts06 prejudica** em BTC e ETH (Sh -1.18 BTC particularly bad). Time stop curto demais corta winners legítimos antes de mean-revert.
2. **ts12 marginal positive em SOL** (+0.36 vs raw), mas sub-gate.
3. **ts24/ts48 ≈ raw** — time stop muito longo (raramente atinge antes de signal natural exit).
4. **raw bollinger 30m FAIL** (Padrão 60 confirms once more — V1 manifests stack canonical não passa em janela longa).

## Decisão

1. **EX001 (time stop curto melhora MR) → GRAVEYARD em Scout.** Nível 1 falhou em todos 3 assets. Top 6 V2 promissora não confirmou.
2. **Padrão 64 (novo)**: time stop curto refutado para bollinger MR canonical. Signal natural mean-cross é exit mais limpo. Time stop curto **prejudica** ao cortar reverte legítimas; time stop longo é no-op (signal já dispara antes).
3. **Manter implementação TimeStopWrapper** — engine novo está pronto, código limpo. Não revertido — outras EX hipóteses (ATR trail, BE-after-MFE, partial TP, MFE decay) podem destravá-lo.
4. **AGENTS.md guideline V2** ratificada — leitura obrigatória pro próximos agentes.

## Padrão 64 (novo)

**EX001 time stop curto refutado para bollinger MR.**

Mecanismo:
- Bollinger MR signal exit (`close >= mu`) ocorre tipicamente em ~5-15 bars na média (mean reverts within range).
- Time stop ts06 corta antes de muitos reverts → winners truncados.
- Time stop ts24/ts48 nunca dispara antes do signal natural → no-op.
- Time stop ts12 marginal em SOL (mais volátil, alguns trades demoram além de 12 bars), neutro/negativo nos outros.

**Implicação:** EX001 não funciona como melhoria simples para MR. Estratégias MR podem precisar exits **vol-aware** (e.g. ATR trail, banda media exit) em vez de time-based.

EX002 (time stop 18 bars) e EX003 (time stop 48 bars) provavelmente similar resultado a ts24/ts48 deste scout — provavelmente também GRAVEYARD por extensão.

## Resumo final V2/RAIO 11 ciclos

- 14 ADRs (0212-0226). 13 padrões (52-64; P57 retroativamente refutado).
- 1 SURVIVOR genuíno (S12 SOL).
- 3 GRAVEYARDs após pipeline completo (P52 individual + P50 cluster coletivo + EX001 family).
- 2 candidatos retirada urgente (S10/S11 paper-trade observation 14d).
- 0 strategies V2 fresh promovidas a manifest.
- ~330 backtests + estatística + portfolio + cross-era + cross-asset + extended + EX001 scout em ~33min wall-clock total.
- **2 engines novos** (BHDrawdownFilter, TimeStopWrapper).
- **AGENTS.md V2 guideline** consolidada (Padrões 53-64).
- **6 datasets concat** + 7 methodology auxiliary files materializados.

## Consequences

- **Positive:** TimeStopWrapper engine instalado, CLI flag funcional. AGENTS.md leitura obrigatória atualizada. Pipeline V2 demonstra capacidade de implementar engines novos rapidamente (~30 min do design ao scout completo).
- **Negative:** EX001 não destrava 36 hipóteses EX coletivamente — apenas refuta time-stop simples. ATR trail / BE / partial TP requerem implementação adicional (TimeStopWrapper é apenas uma das ~10 categorias exit policy).
- **Neutral:** EX001 → GRAVEYARD não bloqueia outras hipóteses EX. Cycle 12+ pode atacar EX004 (ATR trailing) implementando outro wrapper similar.

## Próximas frentes (Cycle 12+ autopilot)

1. **EX004 ATR trailing stop** — implementar `ATRTrailingWrapper` (similar pattern ao TimeStopWrapper). Score ~7.0.
2. **2026-05-10**: ADR-0227 verdict S10/S11 paper-trade observation.
3. **EX009 Break-even after MFE** — implementar `BEAfterMFEWrapper`. Score ~7.0.
4. **Liquidity_trap engine** (LQ001/LQ002 Top 18-19 V2) — biggest gap V2 não-EX. Custo dev maior (~5h).

## Não-alvo

- Não tentar variações EX001 com fees diferentes ou windows diferentes — Padrão 64 já cobre.
- Não tentar EX001 em estratégias trend-following — escopo era MR.
- Não rodar mais probes EX001 sem novo mecanismo causal.

## Padrões totais: 64
