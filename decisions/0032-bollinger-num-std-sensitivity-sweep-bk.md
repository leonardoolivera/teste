# 0032 — Sensibilidade do `num_std` Bollinger: resultados da Série BK e marcação de combos frágeis

**Status:** Superseded — resultados invalidados por ADR-0037, re-derivados em ADR-0038
**Date:** 2026-04-19
**Deciders:** Usuário (owner do projeto) + agente.

> **ERRATA (2026-04-19):** A Série BK original rodou com `regime_filter=bollinger_width:window=20:num_std=2:min_width_bps=250` (defaults do filtro), enquanto o manifest v2 especifica `window=30, num_std=1.5, min_width_bps=250`. ADR-0037 documenta a incidência e ADR-0038 apresenta os resultados com parâmetros corretos. Texto original preservado abaixo para auditoria — **não usar para decisões**. Nova classificação BK em ADR-0038.

## Context

ADR-0028 e ADR-0029 aprovaram 4 combos de deploy no manifest v2 (`bollinger_width_regime_20260418_v2.json`) usando `window=30, num_std=1.5, long_only=True, regime_filter=bollinger_width:min_width_bps=250`:

- ETH 1h 2024-H1
- ETH 1h 2025-H1
- BTC 1h 2024-H2
- SOL 1h 2024-H2

A **Série BK** (`agentic/active/SERIES_BK.md`) testou a hipótese de overfitting paramétrico perturbando `num_std` em ±16.7% (`ns ∈ {1.25, 1.75}`), mantendo window=30, regime gate e contrato runtime-faithful (ADR-0030) fixos. A matriz é 4 combos × 2 perturbações = 8 pilotos (BK.1–BK.8).

Critério decisório pré-estabelecido:
- ≥ 7/8 PASS → Pareto robusto; nota informativa no ADR-0028.
- 4–6/8 PASS → Pareto médio; **este ADR** marca combos frágeis.
- ≤ 3/8 PASS → Pareto estreito; deprecar combos frágeis.

Gates strict aplicados: `trades ≥ 30`, `Sharpe ≥ 1.0`, `MDD ≤ 20%`, `PnL > 0`, `cost_stress_ratio_min ≥ 0.95`, `MC p5 final_equity > 10000`, `MC MDD p95 ≤ 10%`.

## Resultados (resumo em `exports/diag/bk_sweep_summary.json`)

| Tag | Combo | ns | trades | Sharpe | MDD% | PnL% | cost_r | MC p5 eq | MC MDD p95% | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| BK.1 | ETH 2024-H1 | 1.25 | 41 | 2.882 | 1.85 | +7.30 | 0.9814 | 10252 | 3.06 | **PASS** |
| BK.2 | ETH 2025-H1 | 1.25 | 48 | 2.104 | 4.27 | +6.92 | 0.9736 | 10028 | 4.26 | **PASS** |
| BK.3 | BTC 2024-H2 | 1.25 | 35 | 1.325 | 2.53 | +1.97 | 0.9810 |  9904 | 3.28 | FAIL (MC p5) |
| BK.4 | SOL 2024-H2 | 1.25 | 68 | 1.604 | 3.75 | +5.33 | 0.9685 |  9955 | 5.60 | FAIL (MC p5) |
| BK.5 | ETH 2024-H1 | 1.75 | 37 | 0.705 | 3.39 | +1.85 | 0.9830 |  9680 | 5.27 | FAIL (Sharpe, MC p5) |
| BK.6 | ETH 2025-H1 | 1.75 | 41 | 1.961 | 3.91 | +6.52 | 0.9781 | 10030 | 4.90 | **PASS** |
| BK.7 | BTC 2024-H2 | 1.75 | 31 | 1.358 | 2.35 | +2.07 | 0.9824 |  9946 | 3.08 | FAIL (MC p5) |
| BK.8 | SOL 2024-H2 | 1.75 | 62 | 2.229 | 3.70 | +7.33 | 0.9721 | 10194 | 4.82 | **PASS** |

**Placar: 4/8 PASS** → Pareto médio.

Por combo (2 perturbações cada):

| Combo | PASS ns=1.25 | PASS ns=1.75 | Robusto a ±16.7%? |
|---|---|---|---|
| ETH 2024-H1 | ✅ (BK.1) | ❌ (BK.5 Sharpe 0.70) | **Não (assimétrico)** |
| ETH 2025-H1 | ✅ (BK.2) | ✅ (BK.6) | **Sim** |
| BTC 2024-H2 | ❌ (BK.3 MC p5) | ❌ (BK.7 MC p5) | **Não** |
| SOL 2024-H2 | ❌ (BK.4 MC p5) | ✅ (BK.8) | **Não (assimétrico)** |

## Análise

1. **ETH 2025-H1 é o único combo robusto ao eixo `num_std` nos dois lados.** Passa com folga em ambas perturbações (Sharpe 2.10 / 1.96; PnL +6.9% / +6.5%). O ponto `ns=1.5` aprovado pelo ADR-0029 não é singular.

2. **BTC 2024-H2 falha simetricamente** em ambas perturbações no MC p5 (9904 / 9946, ambos abaixo de 10000). Causa raiz: poucos trades (35/31) com PnL médio baixo (+2.0% ao longo do semestre) fazem a cauda 5% do bootstrap cair abaixo do nominal. O gate `MC p5 > 10000` é mais severo para combos "lentos" — isso replica o mesmo padrão do ADR-0029 (BTC 2025-H1 falhou gate #4 por trades<30). **BTC é ativo estruturalmente sensível a perturbação paramétrica neste regime.**

3. **ETH 2024-H1 e SOL 2024-H2 falham assimetricamente.** ETH quebra em ns=1.75 (bandas mais largas → sinais raros → Sharpe colapsa para 0.70). SOL quebra em ns=1.25 (bandas mais estreitas → MC p5 cai para 9955). Indica que o ponto `ns=1.5` está perto da borda do Pareto em um dos lados para cada.

4. **Achado colateral:** BK.1 (ETH 2024-H1 ns=1.25) é **substancialmente melhor** que o baseline ns=1.5 aprovado (Sharpe 2.88 vs 1.83; PnL +7.30% vs +4.68%). Isso **não** motiva mudança do baseline — mudar `num_std` agora seria otimização retroativa sobre validação já consumida (data snooping). O achado vira hipótese para Série futura (BN) com design apropriado (train/validation/test independentes).

## Decision

1. **Manter manifest v2 (ADR-0029) intacto.** Os 4 combos continuam aprovados com `num_std=1.5`. Não há evidência de overfit severo que justifique retirar nenhum combo.

2. **Marcar fragilidade explícita no manifest v2.** Adicionar campo `robustness.num_std_sensitivity` em cada combo do manifest v2:
   - `ETH 2025-H1` → `robust` (passa ambas perturbações).
   - `ETH 2024-H1` → `fragile_high` (falha ns=1.75; lado "largo" é sensível).
   - `SOL 2024-H2` → `fragile_low` (falha ns=1.25; lado "estreito" é sensível).
   - `BTC 2024-H2` → `fragile_both` (falha ambas via MC p5; ativo estruturalmente sensível).

3. **Qualquer rollout futuro (paper/canary/live) deve priorizar ETH 2025-H1** como combo-líder. Combos `fragile_*` entram com peso menor ou sizing reduzido até que pesquisa adicional confirme robustez em outros eixos (window em Série BN, timeframe em BL, regime threshold em BC re-rodada).

4. **Não emitir manifest v3.** A mudança é metadado de robustez (`robustness.*`), não alteração de `approved_combos` ou `engine.params`. Adicionar como amendment ao v2 via novo campo opcional; manifest v2 original preservado (imutável).

5. **Hipótese BK.1 > baseline (ns=1.25 > ns=1.5 em ETH 2024-H1) arquivada como entrada para Série BN** (perturbação de `window`). Não implementar antes de Série BN pelo risco de data snooping.

## Consequences

**Prós:**
- Pareto do eixo `num_std` agora documentado empiricamente, não assumido.
- Combos frágeis explicitamente marcados — proteção contra a próxima release assumir que v2 é uniformemente robusto.
- BTC como classe estrutural "lenta" reconfirmado: qualquer piloto BTC em mean-reversion no futuro precisa de `trades ≥ 30` como gate duro antes de qualquer análise (viés confirmado em ADR-0029 e agora em BK.3/BK.7).

**Contras:**
- Reduz o apetite para usar os 3 combos frágeis em paralelo — efetivamente baixa a expectativa de diversificação do manifest v2.
- Introduz campo de metadata novo (`robustness.*`) que precisa ser respeitado por downstream tooling (bridge, bot, scripts de rollout).

**Riscos residuais:**
- 4/8 é o limite inferior da zona "médio". Se um combo frágil degradar em produção, o resultado de BK corrobora que o risco era conhecido — não é surpresa.
- A Série BK testou apenas **um eixo** (`num_std`). Combos marcados `robust` aqui ainda podem ser frágeis em `window` (BN) ou `timeframe` (BL).

## Follow-ups

- [ ] Atualizar `exports/approved/bollinger_width_regime_20260418_v2.json` com campo `robustness.num_std_sensitivity` por combo.
- [ ] Anexar este ADR como referência cruzada ao ADR-0028 e ADR-0029 (nota informativa).
- [ ] Notificar @botbinance no bridge — rollout futuro deve pesar ETH 2025-H1 como líder.
- [ ] Abrir Série BN (perturbação de `window`) e Série BL (cross-timeframe) para fechar Pareto multi-dimensional antes de qualquer canary.

## Artefatos

- Sweep raw: `results/validation/bk-dryrun-w30-ns{1.25,1.75}-bw250-*` (8 dirs).
- Sweep summary: `exports/diag/bk_sweep_summary.json`.
- Scripts: `tools/run_bk_sweep.py` (sweep), reuso do contrato validate da CLI.
- Série brief: `agentic/active/SERIES_BK.md`.
- Piloto BK.1 detalhado: `agentic/active/bollinger-30-125-eth-1h-2024h1-regime-bw-250/`.
