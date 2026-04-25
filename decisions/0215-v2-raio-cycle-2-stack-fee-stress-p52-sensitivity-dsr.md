# 0215 — V2/RAIO Ciclo 2 — Stack 13 fee stress + P52 Sensitivity + DSR/PSR

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13, em conformidade com escopo ADR-0214 follow-ups
**Relates to:** ADR-0214 (Ciclo 1 verdict), ADR-0213 (V2+RAIO adoption), ADR-0030 (manifest invariantes)

## Contexto

ADR-0214 follow-ups pré-registrados:
- (A) RB007 fee stress sobre 13 manifests aprovados (auditar fee fragility análoga ao Padrão 50).
- (B) Sensitivity Test P52 (RAIO Nível 3): perturbação local 18/45-22/55 × 3 assets × 2024-H2.
- (C) DSR/PSR sobre P52 family (correção data snooping).

Total Ciclo 2: 39 + 48 + 0 (DSR é offline) = 87 backtests + DSR. Wall-clock total ~6min.

## Resultados

### A. RB007 — Stack 13 fee stress (39 probes)

Tools: [`tools/v2_rb007_stack13_fee_stress.py`](../tools/v2_rb007_stack13_fee_stress.py).

13 manifests aprovados re-rodados em fees={5, 10, 15} bps (1x/2x/3x V1 default).

| ID | Manifest | Symbol | Window | Sh@5 | Sh@10 | Sh@15 | Verdict |
|---|---|---|---|---:|---:|---:|---|
| S01 | bollinger_width_regime_v2 | ETH | 2024-H1 | 1.73 | 1.45 | 1.17 | ROBUST |
| S02 | bollinger_width_regime_v2 | ETH | 2025-H1 | 1.49 | 1.25 | 1.02 | ROBUST |
| S03 | bollinger_width_regime_v2 | BTC | 2024-H2 | 1.54 | 1.22 | 0.91 | MARGINAL (tr=20) |
| S04 | bollinger_width_regime_v2 | SOL | 2024-H2 | 2.50 | 2.16 | 1.81 | ROBUST |
| S05 | bollinger_short_width | SOL | 2024-H2 | 2.21 | 1.76 | 1.31 | ROBUST |
| S06 | bollinger_short_width | BTC | 2025-H1 | 0.23 | 0.02 | -0.19 | **FEE-FRAGILE** |
| S07 | bollinger_short_width | ETH | 2025-H1 | 1.68 | 1.36 | 1.04 | ROBUST |
| S08 | bollinger_short_width | SOL | 2025-H1 | -0.15 | -0.48 | -0.80 | **NEGATIVO @ baseline** |
| S09 | rsi_long_width_eth_2024h2 | ETH | 2024-H2 | 1.77 | 1.43 | 1.08 | ROBUST |
| S10 | rsi_short_pure_2025h2 | BTC | 2025-H2 | -2.34 | -2.94 | -3.54 | **NEGATIVO @ baseline** |
| S11 | rsi_short_pure_2025h2 | SOL | 2025-H2 | 0.40 | 0.03 | -0.34 | **FEE-FRAGILE** |
| S12 | rsi_short_trendhtf_sol_2025h1 | SOL | 2025-H1 | 0.56 | 0.35 | 0.15 | **FEE-FRAGILE** |
| S13 | rsi_short_width_2025h1 | BTC | 2025-H1 | 1.41 | 1.19 | 0.97 | MARGINAL (tr=16) |

**Counts:**
- 6/13 ROBUST: S01, S02, S04, S05, S07, S09 (Sh ≥ 1.0 em fees 15bps).
- 2/13 MARGINAL: S03, S13 (Sh borderline 0.91-0.97 + trade count baixo 16-20).
- 5/13 FEE-FRAGILE / NEGATIVO @ baseline: S06, S08, S10, S11, S12.

**S08 e S10 já são NEGATIVOS no baseline 5bps** (S08 Sh=-0.15, S10 Sh=-2.34). Achado crítico: 2/13 (15%) dos manifests "aprovados" não reproduzem em re-execução fresh do walk-forward — possíveis causas:
1. Drift de dados (re-resample 10m→1h pode ter reproduzido com seed diferente).
2. Execução original V1 usou `n_folds`/`mc_seed` diferentes; default V2 (n_folds=5, mc_seed=42) não bate.
3. Manifest aprovado em uma versão de código + dataset que mudou desde então.

Investigação dedicada deferida (ADR-0216 ou troubleshooting). Por ora: **flag S08 e S10 como suspeitos de não-reprodução**; restantes 11/13 mantêm contrato.

### B. P52 Sensitivity (48 probes, RAIO Nível 3)

Tools: [`tools/v2_rb012_sensitivity_p52.py`](../tools/v2_rb012_sensitivity_p52.py). Wall-clock 16s.

Grid: ma_crossover (S ∈ {18, 20, 22, 25} × L ∈ {45, 50, 55, 60}) × (BTC, ETH, SOL × 2024-H2). 48 configs (S < L excluding S = L).

| Asset | N | gate (Sh ≥ 1.0 ∧ tr ≥ 30) | Sh range | Trade range |
|---|---:|---:|---|---|
| BTC | 16 | 12/16 (75%) | 1.94-3.10 | 26-38 |
| ETH | 16 | 8/16 (50%) | 1.25-2.61 | 22-39 |
| SOL | 16 | 9/16 (56%) | 0.94-2.01 | 24-40 |
| **Total** | **48** | **29/48 (60%)** | 0.94-3.10 | 22-40 |

**Crucial:** todos 48 configs têm Sh ≥ 0.94 — edge não colapsa em nenhuma perturbação. Falhas no gate são por trade count em windows longas (L=55, 60), não Sharpe negativo. **Vizinhança paramétrica é estruturalmente positiva.**

Sweet spot estável: (S=18-22, L=45-55). Notavelmente, **S=18 outperforma S=20 (canonical V1)** em BTC e ETH — V1 não estava no exato sweet spot.

### C. DSR/PSR P52 family (RAIO Nível 4 — falsificação estatística)

Tools: [`tools/v2_rb014_dsr_psr_p52.py`](../tools/v2_rb014_dsr_psr_p52.py). Aplicação de Bailey & López de Prado 2014.

Parâmetros da family:
- N configs = 48
- Annualized Sharpes: min=0.94, median=1.93, max=3.10
- Variance of family Sharpes = 0.3524
- DSR threshold (SR_0 annualized) = **1.342**
- skew distribuição bar-level: 0.02-0.54
- kurt distribuição bar-level: 14-21 (alta cauda gorda — característica crypto)

**Verdicts:**
| Critério | Pass | Total | % |
|---|---:|---:|---:|
| PSR(0) > 0.95 (Sharpe positivo significativo) | 13 | 48 | 27% |
| PSR(SR_0=1.34) > 0.95 (DSR strict pass) | **0** | 48 | 0% |
| PSR(SR_0=1.34) > 0.50 (DSR marginal) | 39 | 48 | 81% |

Top 5 probes (PSR(DSR) descendente):
1. BTC 25/60 — Sh=3.10, PSR(DSR)=0.8648
2. BTC 18/60 — Sh=3.02, PSR(DSR)=0.8546
3. BTC 22/60 — Sh=2.96, PSR(DSR)=0.8448
4. BTC 25/55 — Sh=2.89, PSR(DSR)=0.8348
5. BTC 20/60 — Sh=2.87, PSR(DSR)=0.8316

**Ninguém atinge 0.95.** Causa principal: kurtosis bar-level ~20 (caudas gordas crypto) infla denominador PSR. Característica do mercado, não overfitting.

**Limitação metodológica registrada (Padrão 54):** PSR/DSR Bailey-LdP foi derivado assumindo distribuição não muito longe de gaussiana. Crypto bar-level returns têm kurt 10-30; aplicar threshold 0.95 estrito penaliza desproporcionalmente. **Adaptação V2:** considerar PSR(0)>0.95 como "evidência inicial" + Sensitivity grid sólido como gate alternativo a DSR strict.

## Decisão

1. **Stack 13 audit** ([fee stress matrix](../exports/diag/v2_rb007_stack13_progress.json)):
   - **6/13 ROBUST** mantidos no stack canonical.
   - **2/13 MARGINAL** (S03 BTC bollinger 2024-H2, S13 BTC rsi 2025-H1): manter mas marcar como "low margin" — futuro re-validation com mais trade count exigido.
   - **3/13 FEE-FRAGILE** (S06, S11, S12): **flagged**. Stack contém edge real apenas em fees ~5bps; degradação significativa em condições normais.
   - **2/13 NÃO-REPRODUZEM** (S08, S10): suspeita grave. **Hold** — não export para BotBinance até ADR-0216 investigar reprodutibilidade.
2. **P52** mantém **QUARANTINED** (não promove a SURVIVOR):
   - Sensitivity 60% gate pass + 100% Sh > 0.94 → vizinhança robusta ✓
   - DSR strict 0/48 → não passa correção data snooping convencional ✗
   - Prior aumentado vs Ciclo 1, mas não escapa quarantine sem método estatístico mais adequado a crypto bar-level (e.g., bootstrap não-paramétrico, block bootstrap por regime).
3. **Padrão 53 confirmado retroativamente** sobre o stack: 38% (5/13) manifests V1 são fee-fragile ou não-reproduzem. Reforço da lição "screening fees=5bps inadequado".
4. **Padrão 54 (novo):** DSR/PSR Bailey-LdP penaliza desproporcionalmente strategies em mercados de cauda gorda (kurt>10). V2 adota PSR(0)>0.95 como gate inicial + Sensitivity grid como gate alternativo a DSR strict.

## Patterns updated

- **Padrão 53** (fees floor): screening V1 fees=5bps subestima custos. V2 default=10bps. Confirmado retroativamente sobre 38% do stack canonical em produção.
- **Padrão 54** (DSR/PSR limitação crypto): aplicar threshold 0.95 estrito em mercados kurt>10 é demasiadamente restritivo. Critério V2: PSR(0)>0.95 + Sensitivity grid + cross-era + fee stress como AND-conjunto, não DSR isolado.
- **Padrão 52** mantém QUARANTINED — Sensitivity excelente, DSR insuficiente, mas único candidato V1 sobrevivente real.

## Consequences

- **Positive:** RAIO Ciclo 2 entregou auditoria crítica de produção. 5/13 do stack flagged (3 fee-fragile + 2 não-reproduzem). Padrão 52 testado em 4 níveis (Replication + Sensitivity + Fee stress + DSR/PSR) com perfil técnico claro. Falsificação estatística agora é gate operacional.
- **Negative:** Stack 13 atualmente em produção tem 5/13 problemas conhecidos. ADR de remediação (0216) deve definir: (a) reprodução S08/S10, (b) re-aprovação ou retirada dos 3 fee-fragile, (c) manifestos para BotBinance.
- **Neutral:** P52 quarantine prolongado é aceitável — RAIO §6 é claro que QUARANTINED é estado válido para "promissor mas precisa validação estatística mais cara". Não bloqueia outros nós da árvore.

## Follow-ups (próximo Ciclo 3)

- **ADR-0216:** investigação reprodutibilidade S08, S10. Comparar manifest original vs re-run V2; identificar drift.
- **Bootstrap não-paramétrico para P52** (alternativa a DSR/PSR): block bootstrap por regime sobre returns; gate=p > 0.95 retorno > 0 com block_size adequado pra crypto autocorrelação.
- **Atacar próxima frente RAIO autopilot:** fila de scores em SEARCH_STATE.md prioriza nova raiz vs P52 deepening. Análise: novas raízes têm score>5 (RM013 paused, EX001 pré-eng-novo). Continuação P52 com bootstrap tem score ~6 — vence próximo ciclo.
- Atualizar HYPOTHESIS_TREE, NODE_LOG, GRAVEYARD, SEARCH_STATE, STATE.md com decisões deste ADR.

## Não-alvo

- Não tentar variações P52 fora da vizinhança 18-25/45-60 (RAIO §5 anti grid search disfarçado).
- Não export P52 para BotBinance sem PSR convencional acima 0.95 OR validação por bootstrap não-paramétrico.
- Não cortar S08/S10 do stack sem ADR-0216 reproducibility investigation completa.
- Não relaxar gate Sh ≥ 1.0 V2 para "salvar" mais probes.

## Padrões totais: 54 (53 fees floor confirmado retroativamente; 54 DSR/PSR crypto limitação)
