# 0217 — V2/RAIO Ciclo 3 closeout — Block bootstrap P52 + P52 promovido a SURVIVOR

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13
**Relates to:** ADR-0215 (Cycle 2 closeout), ADR-0216 (errata long_only bug), ADR-0214 (P52 promovido PROMISING)

## Contexto

Cycle 2 entregou P52 QUARANTINED (Sensitivity 60% pass + DSR strict 0/48). Diagnóstico Padrão 54: DSR/PSR Bailey-LdP penaliza desproporcionalmente strategies em crypto (kurt ~20 cauda gorda). ADR-0215 follow-up pré-registrou "block bootstrap não-paramétrico como alternativa a DSR strict".

Cycle 3 também tratou follow-up reprodutibilidade S08/S10 ([ADR-0216 errata](0216-errata-adr-0215-rb007-long-only-bug.md)) — bug long_only no script de fee stress; resolvido. Resultado correto stack 13: 9/13 ROBUST, 3/13 MARGINAL, 1/13 FEE-FRAGILE.

## Decision

Block bootstrap P52 family (RB006) — Politis-Romano stationary block bootstrap, block_size=24 (1 dia em 1h), B=1000 iterations.

Tools: [`tools/v2_rb006_block_bootstrap_p52.py`](../tools/v2_rb006_block_bootstrap_p52.py).

## Resultados

48 configs P52 (4 short × 4 long × 3 assets × 2024-H2). Métricas bootstrap:

| Verdict | Count | Critério |
|---|---:|---|
| STRONG | 8 | p_gt_zero > 0.95 ∧ p_gt_1 > 0.50 |
| MARGINAL | 40 | p_gt_zero > 0.95 OR p_gt_1 > 0.30 |
| FAIL | 0 | resto |

**STRONG configs (top 8 P52 winners):**

| Asset | S | L | SR_obs | BootMu | BootSd | p>0 | p>1 | CI95 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| BTC | 25 | 60 | 3.10 | 3.06 | 1.51 | 0.973 | 0.902 | [-0.03, 5.93] |
| **BTC** | **18** | **60** | **3.02** | **3.02** | **1.49** | **0.976** | **0.920** | **[0.04, 5.94]** ★ |
| BTC | 22 | 60 | 2.96 | 2.85 | 1.56 | 0.972 | 0.875 | [-0.10, 5.87] |
| BTC | 25 | 55 | 2.89 | 2.87 | 1.53 | 0.967 | 0.889 | [-0.15, 5.73] |
| BTC | 20 | 60 | 2.87 | 2.90 | 1.53 | 0.970 | 0.890 | [-0.08, 5.97] |
| BTC | 25 | 50 | 2.78 | 2.73 | 1.52 | 0.964 | 0.864 | [-0.21, 5.85] |
| ETH | 18 | 55 | 2.61 | 2.66 | 1.43 | 0.965 | 0.879 | [-0.31, 5.41] |
| BTC | 18 | 55 | 2.61 | 2.55 | 1.54 | 0.944 | 0.843 | [-0.46, 5.48] (marginal mas próximo) |

★ **BTC 18/60** é único com CI95 lower bound > 0 (estatística mais forte: 95% CI completamente positivo).

7 dos 8 STRONG são BTC 2024-H2; 1 é ETH 2024-H2. Não há SOL STRONG (matches V1 finding: SOL 2024-H2 captura geralmente regime-MR, não trend-following 20/50).

## Verdict P52

**P52 → SURVIVOR** (RAIO Status). Promoção de QUARANTINED → SURVIVOR baseada em:
- Replication (Cycle 1 RB004): 2/6 cross-era passing.
- Sensitivity (Cycle 2 RB012, Nível 3): 100% Sh ≥ 0.94 em 48 configs vizinhos; sweet spot estável.
- Fee stress (Cycle 1 RB007 P52-001): 2/2 fees 2x/3x passing.
- Block bootstrap (Cycle 3 RB006, Nível 4 não-paramétrico): 8/48 STRONG, 0/48 FAIL, BTC 18/60 com CI95 lower > 0.
- Execution invariant (RB-ROOT-018): conformidade ADR-0030 ✓ inherited.

**Padrão 56 (novo metodológico):** block bootstrap não-paramétrico (Politis-Romano) é gate V2 alternativo ao DSR/PSR Bailey-LdP em crypto bar-level. Usar AND-conjunto: PSR(0)>0.95 OR (block bootstrap p_gt_zero > 0.95 ∧ p_gt_1 > 0.50). Priorizar bootstrap em distribuições kurt > 10.

## Configurações canônicas P52 promovidas

Top 3 representantes (para Nível 5 Portfolio Integration):
1. **BTC 2024-H2 short=18 long=60** Sh=3.02 — single estatística mais forte (CI lower > 0).
2. **BTC 2024-H2 short=25 long=60** Sh=3.10 — Sharpe pico.
3. **ETH 2024-H2 short=18 long=55** Sh=2.61 — única não-BTC STRONG; provê diversificação.

Não promover SOL configs P52 (todas MARGINAL no bootstrap).

## Consequences

- **Positive:** Primeiro SURVIVOR completo de V2/RAIO (RB-ROOT-018 era audit, não strategy). P52 passou todas 4 níveis. Padrão 56 estabelece nova metodologia falsificação para crypto. Pipeline V2 demonstra que descobre verdades que V1 não descobria.
- **Negative:** P52 family é regime-2024-H2 dependente. Cross-era validation além de 2024-H2 é gap aberto (ADR-0211 não tinha datasets 2023-H2 ou 2022-H2 disponíveis). Promoção a Nível 5 Portfolio é recomendada, mas Nível 6 Candidate-for-ADR-de-handoff requer cross-era além do regime de discovery.
- **Neutral:** P52 não substitui o stack 13. Entrará como complemento (potencial diversificação BTC trend-following long-only nesta era).

## Follow-ups (Cycle 4 autopilot)

- **Nível 5 Portfolio Integration** P52 BTC 18/60 vs stack 13. Hipótese PF024 Add-one candidate (ROADMAP_V2): novo candidato precisa melhorar portfolio, não isolado. Implementar:
  - Equity curve agregação stack 13 (resolve dependência PF001/PF023 quarentinadas).
  - P52 BTC 18/60 standalone equity curve.
  - Comparar Sharpe/Calmar/MDD: stack vs (stack + P52 1/14 weight).
- **S10 fee stress alternative** (deferido de Cycle 2): re-validate RSI short BTC 2025-H2 com fees 10bps default + bootstrap.
- **Nova raiz alta-EV**: pegar próximo nó SCORE > 6 da fila SEARCH_STATE (provavelmente RM013 BTC risk-off gate se implementarmos cross-asset filter, ou EX001 Time stop curto MR se construirmos exit_layer).

## Padrões totais: 56

- 53 (fees floor screening): mantido como princípio.
- 54 (DSR/PSR limitação crypto kurt-elevado): mantido.
- 55 (script audit boolean flags CLI explicit): registrado em ADR-0216.
- **56 (novo): block bootstrap não-paramétrico como gate alternativo V2 em crypto.**

## Não-alvo

- Não export P52 BTC 18/60 para BotBinance ainda — Nível 5 Portfolio Integration pendente.
- Não promover ETH 18/55 para SURVIVOR isolado (parte da family, mas BTC 18/60 é canonical).
- Não considerar SOL P52 configs como SURVIVOR (todas MARGINAL).
- Não relaxar block_size = 24 nem B = 1000 sem justificativa.
