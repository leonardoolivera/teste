# NODE_LOG

**Updated:** 2026-04-25
**Protocol:** LIGHTNING_SEARCH_PROTOCOL.md (RAIO §11)

> Diário append-only. Cada execução de nó RAIO registra entry abaixo. Nunca apagar entries; só adicionar.

---

## 2026-04-25 — Bootstrap V2+RAIO

- action: ROOT_REGISTRATION
- nodes_created: RB-ROOT-018, PF-ROOT-001, PF-ROOT-023, RM-ROOT-013
- nodes_quarantined_from_v1: P50-Q-001, P51-Q-001, P52-Q-001
- backlog_roots_registered: EX-ROOT-001..036, PS-ROOT-001..027, LQ-ROOT-001..027, RM-ROOT-001..036, PF-ROOT-002..022/024..027, XP-ROOT-001..009
- decision: ADR-0212 (V1 closeout) + ADR-0213 (V2+RAIO adoption)
- decision_reason: V1 cobertura runnable esgotada (658/1000); V2+RAIO methodologically superior; padrões V1 single-window não promovem.
- files_affected: HYPOTHESIS_TREE.md (created), NODE_LOG.md (this file), SEARCH_STATE.md (created), GRAVEYARD.md (created), decisions/0212-roadmap-1000-v1-closeout-pivot-v2.md, decisions/0213-v2-raio-adoption-prereg.md
- next_node: RB-ROOT-018 Scout
- notes: 658 r1k-* runs preservados em results/validation/ como input para auditoria RB018 e portfolio aggregation PF001/PF023.

## 2026-04-25 — RB-ROOT-018 Scout

- node_id: RB-ROOT-018
- action: SCOUT (Nível 1)
- validation_level: 1 → effectively cobre Nível 4 robustness (audit estatístico sobre 658 walk-forward runs)
- result: 658/658 runs clean (100%); 0 violations across 4 ADR-0030 invariants (bar offset, missing timestamp, notional drift, stop loss present)
- key_metrics:
    n_runs_audited: 658
    n_clean: 658
    n_dirty: 0
    aggregate_violations: {}
- decision: VALIDATE → SURVIVOR
- decision_reason: Todos os 658 r1k V1 runs respeitam invariantes ADR-0030 (entry/exit fill = market@open[t+1]; sizing literal fixed_notional 2000.0; sem stop_loss). Audit confirma que V1 dispatcher (run_roadmap_auto.py) opera corretamente; runs servem como input válido para PF001/PF023/análises portfolio futuras.
- files_affected: tools/v2_rb018_execution_invariant_audit.py (created), exports/diag/v2_rb018_audit.json (created), HYPOTHESIS_TREE.md (RB-ROOT-018 → SURVIVOR), SEARCH_STATE.md
- next_node: PF-ROOT-001
- notes: Foi possível pular Nível 1→4 porque RB018 é audit estatístico, não estratégia testada incrementalmente.

## 2026-04-25 — PF-ROOT-001 / PF-ROOT-023 — re-evaluation

- nodes: PF-ROOT-001, PF-ROOT-023
- action: RE_SCOPE
- validation_level: 0
- result: Pre-Scout discovery — `fixed_100_stack13_20260422.json` contém apenas stats agregados (Sharpe, PnL%, MDD) por combo, NÃO equity curves alinhadas necessárias para portfolio aggregation real.
- decision: QUARANTINE (PAUSED até infra de aggregação)
- decision_reason: PF001 (equal-weight portfolio) e PF023 (one-combo-out ablation) requerem equity curves time-aligned cross-combo. Stats agregados permitem média de Sharpe mas não simulação de portfolio real (sem matriz de correlação ou retornos por barra). Implementar agregador é dev de média complexidade; antes de gastar nisso, pivotar para alta-EV cross-era validation.
- files_affected: SEARCH_STATE.md, HYPOTHESIS_TREE.md
- next_node: RB-ROOT-013 → re-evaluation

## 2026-04-25 — RM-ROOT-013 — re-evaluation

- node_id: RM-ROOT-013
- action: RE_SCOPE
- validation_level: 0
- result: Filtro `btc_return_24h<0` requer cross-asset signal (BTC dataset alongside running asset) + nova classe `CrossAssetReturnFilter` em `src/alpha_forge/regimes/filter.py`.
- decision: PAUSE (engine novo)
- decision_reason: Implementação ~50-100 LoC + tests, mas gate single causal pra todos RM001-036 que precisam multi-asset. Vale ADR dedicado antes de implementar. Não bloqueia próximo nó alta-EV (cross-era validation V1 winners).
- files_affected: SEARCH_STATE.md
- next_node: RB-ROOT-004+007 sobre Padrões 50/51/52

## 2026-04-25 — V2-RB004+RB007 over V1 winners (Padrões 50/51/52)

- nodes_grouped: P50-Q-001, P51-Q-001, P52-Q-001 cross-era + fee stress
- action: SCOUT (Nível 2 Replication + parte do Nível 4 Robustness)
- validation_level: 2-4 (replication + fee stress)
- script: tools/v2_rb004_rb007_v1_winners_validation.py
- jobs: 9 V1 configs × (6 cross-era windows + 2 fee stress=2x/3x) = ~72 probes
- decision: pending (running)
- decision_reason: Padrões V1 quarentinados todos single-window. Cross-era + fee stress são os 2 cortes mais agressivos do RAIO Nível 2-4. Se >50% configs perdem gate em cross-era → enterrar Padrões; se <30% perdem → promover candidates por nível.
- files_affected: tools/v2_rb004_rb007_v1_winners_validation.py (created), exports/diag/v2_rb004_rb007_progress.json (will be created), exports/diag/v2_rb004_rb007.log (running)
- next_node: post-result analysis

## 2026-04-25 — Ciclo 2.A: RB007 stack13 fee stress

- nodes: S01..S13 (13 manifests aprovados, 39 jobs com fees 5/10/15bps)
- action: SCOUT (Nível 4 Robustness — fee stress)
- script: tools/v2_rb007_stack13_fee_stress.py
- result: 6/13 ROBUST (S01,S02,S04,S05,S07,S09); 2/13 MARGINAL (S03,S13); 3/13 FEE-FRAGILE (S06,S11,S12); 2/13 NEGATIVO @ baseline (S08,S10)
- decision: RB007 SURVIVOR (audit completo); FLAG S06/08/10/11/12 para ADR-0216 remediação
- decision_reason: 38% do stack 13 não passa fee stress 15bps; 15% nem reproduz baseline. Padrão 53 (fees floor) confirmado retroativamente sobre produção.
- files_affected: tools/v2_rb007_stack13_fee_stress.py, exports/diag/v2_rb007_stack13_progress.json
- next_node: P52 Sensitivity

## 2026-04-25 — Ciclo 2.B: P52 Sensitivity (RAIO Nível 3)

- node: P52-Q-001
- action: SENSITIVITY_TEST (Nível 3)
- script: tools/v2_rb012_sensitivity_p52.py
- jobs: 48 (4 short × 4 long × 3 assets, S<L)
- result: 29/48 pass gate (Sh≥1.0 ∧ tr≥30); 100% Sh ≥ 0.94 (edge não colapsa em nenhuma config)
- key_metrics:
    BTC 2024-H2: 12/16 pass, Sh range 1.94-3.10
    ETH 2024-H2: 8/16 pass, Sh 1.25-2.61 (fails por trade count em windows longas)
    SOL 2024-H2: 9/16 pass, Sh 0.94-2.01
- decision: PROCEED to DSR/PSR (Nível 4)
- decision_reason: vizinhança paramétrica completa positiva → P52 não é sweet-spot frágil; pode prosseguir para falsificação estatística.
- files_affected: tools/v2_rb012_sensitivity_p52.py, exports/diag/v2_rb012_sensitivity_p52_progress.json
- next_node: DSR/PSR

## 2026-04-25 — Ciclo 2.C: DSR/PSR P52 family (RAIO Nível 4)

- node: P52-Q-001
- action: DSR_PSR_TEST (Nível 4 falsificação estatística)
- script: tools/v2_rb014_dsr_psr_p52.py (Bailey & Lopez de Prado 2014)
- result:
    PSR(0)>0.95: 13/48 (27%)
    PSR(SR_0=1.34)>0.95: **0/48 (0%)** — DSR strict não passa
    PSR(SR_0)>0.50: 39/48 (81%) — DSR marginal
- top: BTC 25/60 Sh=3.10 PSR(DSR)=0.86; BTC 18/60 Sh=3.02 PSR(DSR)=0.85
- decision: P52 mantém QUARANTINED (RAIO §6)
- decision_reason: kurt bar-level ~20 (cauda gorda crypto) infla denominador PSR; DSR strict é demasiadamente restritivo neste regime. **Padrão 54 registrado**: DSR/PSR Bailey-LdP penaliza desproporcionalmente crypto. V2 adota PSR(0)>0.95 + Sensitivity sólida + cross-era + fee stress como AND-conjunto.
- files_affected: tools/v2_rb014_dsr_psr_p52.py, exports/diag/v2_rb014_dsr_psr_p52.json
- next_node: ADR-0215 closeout Ciclo 2 + planejar Ciclo 3 (bootstrap não-paramétrico + investigação S08/S10)

## 2026-04-25 — Ciclo 3.A: ADR-0216 errata (long_only bug fix)

- nodes: S01..S13 (re-run completo após fix)
- action: BUG_FIX + RE_RUN
- bug: `tools/v2_rb007_stack13_fee_stress.py` não passava `--no-long-only` para combos SHORT; CLI default = long_only=True; 8/13 combos rodaram como LONG.
- fix: pass `--long-only` explicitamente em ambos paths.
- result: 9/13 ROBUST, 3/13 MARGINAL, 1/13 FEE-FRAGILE (S10), 0/13 NEGATIVO. S08 Sh=2.71 reproduz manifest (2.713 ✓), S10 Sh=1.64 = 1.64 ✓.
- decision: ERRATA ADR-0215 §A (stack 13 audit). §B e §C NÃO afetados.
- decision_reason: leitura ADR-0215 "5/13 problemas (38%)" inválida. Conclusão correta: stack 13 majoritariamente robusto (9/13 = 69%). Padrão 53 mantido como princípio mas escopo retroativo correto = 1/13 (8%) fragile.
- new_pattern: **Padrão 55** — script audit obrigatório, todo script V2/RAIO passa boolean flags CLI explicitamente.
- files_affected: tools/v2_rb007_stack13_fee_stress.py (fix), exports/diag/v2_rb007_stack13_progress.json (re-run), decisions/0216-errata-adr-0215-rb007-long-only-bug.md
- next_node: re-evaluation Ciclo 3 — agora que stack está saudável, próxima frente é Ciclo 3.B (block bootstrap P52) ou nova raiz

## 2026-04-25 — Ciclo 3.B: Block bootstrap P52 (RAIO Nível 4 alternativo)

- node: P52-Q-001
- action: BOOTSTRAP_TEST (Politis-Romano stationary block bootstrap)
- script: tools/v2_rb006_block_bootstrap_p52.py
- params: block_size=24 (1 dia em 1h), B=1000 iterations, seed=42
- result: 8/48 STRONG, 40/48 MARGINAL, 0/48 FAIL
- top STRONG: BTC 18/60 Sh=3.02 p>0=0.976 p>1=0.920 CI95=[0.04, 5.94] ★ unico CI lower > 0
- 7 dos 8 STRONG são BTC 2024-H2; 1 é ETH 2024-H2; 0 SOL.
- decision: P52-Q-001 promoted QUARANTINED → **SURVIVOR**
- decision_reason: P52 passou todos 4 níveis: Replication + Sensitivity + Fee stress + Block bootstrap. DSR strict tinha sido restritivo demais (Padrão 54); bootstrap não-paramétrico é alternativa adequada (Padrão 56 novo).
- new_pattern: **Padrão 56** — block bootstrap não-paramétrico (Politis-Romano) como gate V2 alternativo a DSR/PSR Bailey-LdP em crypto kurt-elevado.
- files_affected: tools/v2_rb006_block_bootstrap_p52.py, exports/diag/v2_rb006_block_bootstrap_p52.json, decisions/0217-v2-raio-cycle-3-block-bootstrap-p52-survivor.md, HYPOTHESIS_TREE.md
- next_node: Nível 5 Portfolio Integration P52 BTC 18/60 vs stack 13 (PF024 add-one candidate)

## 2026-04-25 — Ciclo 4: PF024 Add-one P52 (RAIO Nível 5)

- node: P52-Q-001 (Padrão 52 BTC 18/60)
- action: PORTFOLIO_INTEGRATION (Nível 5)
- script: tools/v2_pf024_addone_p52_vs_stack13.py
- jobs: 14 runs (stack 13 + P52) sobre janela comum 2024-H2; cada combo no seu asset original. Wall=21s.
- result: PF024 PASS — todos 4 eixos melhoram
- key_metrics:
    Stack 13 EW: Sh=0.57, Calmar=0.64, MDD=4.46%, PnL=1.11%
    Stack 14 (+P52 1/14): Sh=0.91 (+60%), Calmar=1.19 (+87%), MDD=3.55% (-20%), PnL=1.65%
    P52 standalone: Sh=3.02, Calmar=10.36, MDD=2.29%, PnL=8.76%
- correlations: P52 corr S10=-0.60, S13=-0.38, S06=-0.28, S11=-0.27 → hedge estrutural shorts
- decision: P52 SURVIVOR → **Candidate for ADR (Nível 6)** but **NOT exportable** sem cross-era 2024-H1 + 2023-H2
- new_pattern: **Padrão 57** — trend-following long-only como hedge estrutural para stack short/MR cripto 2024-H2
- files_affected: tools/v2_pf024_addone_p52_vs_stack13.py, exports/diag/v2_pf024_addone_p52.json, decisions/0218-v2-raio-cycle-4-pf024-p52-portfolio-integration-pass.md, HYPOTHESIS_TREE.md
- next_node: Cycle 5 — cross-era 2024-H1 + 2023-H2 P52 (12 probes, ~3min); gate pré-export ADR-0030

## 2026-04-25 — Ciclo 5: P52 cross-era gate ADR-0030 (RAIO Nível 4 final)

- node: P52-Q-001
- action: CROSS_ERA_GATE (Nível 4 final pré-Nível 6 promotion)
- script: tools/v2_rb004_p52_cross_era_gate.py
- jobs: 24 probes (3 assets × 4 windows non-discovery × 2 fees). Wall=11s.
- result: 1/12 pass com fees 10bps (SOL 2023-H2 Sh=3.46). Bear 2022 catastrófico (-2.18 a -2.85). Cross-era 2024-H1 marginal (≤1.44, tr<30 SOL).
- gate ADR-0030 (≥2 windows × ≥2 assets): **FAIL** (0 windows com ≥2 assets passando).
- decision: P52 DOWNGRADE Candidate-for-ADR → **QUARANTINED regime-2024 only**. NÃO export.
- new_pattern: **Padrão 58** — trend-following long-only crypto é regime-conditional (bull/recovery only); bear absoluto causa drawdown 6-12%; standalone sem regime gate proibido em produção.
- meta-lesson: PF024 PASS isolado não é gate suficiente sem cross-era. Adotar V2: PF024 deve rodar em ≥2 regimes distintos antes de promoção Nível 6.
- files_affected: tools/v2_rb004_p52_cross_era_gate.py, exports/diag/v2_rb004_p52_cross_era_gate.json, decisions/0219-v2-raio-cycle-5-p52-cross-era-fail-regime-conditional.md, HYPOTHESIS_TREE.md
- next_node: Cycle 6 — implementar regime detector (RM013 BTC risk-off OR RM034 B&H DD gate) OR implementar exit_layer (EX001 Top 6 V2)

## 2026-04-25 — Cycle 6: BHDrawdownFilter implementado + Padrão 59

- node: Padrão 58 mitigation infra
- action: ENGINE_NEW (BHDrawdownFilter)
- script: src/alpha_forge/regimes/filter.py + tools/v2_rb004_p52_with_bh_drawdown_gate.py
- result: filter funcional, round-trip OK; P52+gate cross-era 6m: drawdowns -90% mas trade count <30 → Padrão 59
- decision: continue Cycle 7 com janela contínua 30 meses
- new_pattern: **Padrão 59** — regime gate apertado vs sample size tradeoff em windows curtas
- files: decisions/0220-v2-raio-cycle-6-bh-drawdown-filter-impl-padrao-59.md
- next_node: Cycle 7

## 2026-04-25 — Cycle 7: Janela contínua 30m + P52 GRAVEYARD final

- node: P52-Q-001 (final verdict)
- action: EXTENDED_WINDOW_TEST (Nível 4 final under Padrão 60)
- scripts: tools/v2_concat_extended_datasets.py, tools/v2_p52_gate_extended_window.py
- jobs: concat 3 assets × 5 semestres = 21672 bars; 12 probes (3 assets × 4 variants); wall=17s
- result: 0/12 pass gate; bh_drawdown(15%) reduz MDD 14→6 (ETH), 17→6 (SOL) MAS Sh ≤ 0.87 todos
- decision: P52 → **GRAVEYARD** após 7 ciclos
- decision_reason: edge Sh=3.02 era selection bias temporal (intra-2024-H2). Janela contínua 30m: Sh ≈ 0. Padrão 58 mitigation funciona (-60% MDD) mas P52 não tem signal robusto cross-regime.
- new_pattern: **Padrão 60** — janela contínua ≥18m é mandatória para promoção V2; windows curtas inflacionam Sharpe via temporal selection bias
- files: decisions/0221-v2-raio-cycle-7-p52-graveyard-extended-window-verdict.md, GRAVEYARD.md, HYPOTHESIS_TREE.md, STATE.md
- next_node: Cycle 8 — audit retroativo stack 13 sob Padrão 60 (reusa concat datasets)

## 2026-04-25 — Cycle 8: Stack 13 audit Padrão 60 (92% FAIL)

- nodes: S01..S13
- action: PADRAO_60_AUDIT (retroativo)
- script: tools/v2_stack13_padrao60_audit.py
- result: 1/13 ROBUST (S12 rsi_short_trendhtf SOL Sh=1.20); 3/13 MARGINAL (S01-S03 bollinger_width_regime_v2); 9/13 FAIL incluindo 3 com PnL negativo (S09, S10, S11)
- catastrophic finds: S10 BTC rsi_short_pure 2025h2 Sh=-0.58 MDD=22% PnL=-12%; S11 SOL Sh=-0.38 MDD=36% PnL=-17%
- decision: stack canonical V1 é selection-bias-fragile; flag S10+S11 para retirada após paper-trade observation extended
- new_pattern: **Padrão 61** — Stack canonical V1 era construído por seleção temporal local; em janela contínua 30m, 92% perdem edge
- files: decisions/0222-v2-raio-cycle-8-stack13-padrao60-audit-92pct-fail.md, HYPOTHESIS_TREE.md, STATE.md
- next_node: Cycle 9 — cross-asset S12 (testar generalização)

## 2026-04-25 — Cycle 9: S12 cross-asset FAIL (SOL-specific) + consolidação P53-62

- node: S12-survivor → cross-asset validation
- action: CROSS_ASSET_TEST + CONSOLIDATION
- script: tools/v2_s12_cross_asset_validation.py
- result: 1/3 pass (SOL Sh=1.20, BTC -0.02, ETH -0.01)
- decision: S12 SOL-specific confirmado; mantém SURVIVOR escopo SOL-only; não promove cross-asset
- new_pattern: **Padrão 62** — asset-specific edges são raros mas legítimos em crypto; SOL microstructura idiossincrática permite RSI+HTF gate
- consolidation: methodology guideline V2 = Padrões 53-62 (9 padrões metodológicos consolidados)
- final summary 9 ciclos: 12 ADRs, 11 padrões, 1 SURVIVOR (S12), 1 GRAVEYARD pipeline-completo (P52), 2 retirada candidates (S10/S11), 0 strategies novas promovidas
- files: decisions/0223-v2-raio-cycle-9-s12-sol-specific-padroes-consolidados.md, STATE.md
- next_node: Cycle 10 — ADR-0224 paper-trade observation S10/S11 OR implementar exit_layer engine

## 2026-04-25 — Cycle 10.A: ADR-0224 paper-trade observation S10/S11

- nodes: S10, S11 (rsi_short_pure_2025h2 BTC + SOL)
- action: OPERATIONAL_PROTOCOL (não backtest)
- decision: Não retirar imediatamente; protocolo 14 dias observation com sinais explícitos retirada
- timeline: 2026-04-26 início → 2026-05-03 mid-check → 2026-05-10 ADR-0226 verdict
- files: decisions/0224-stack13-paper-trade-observation-s10-s11-pre-removal.md
- next_node: Cycle 10.C audit Padrão 50 V1

## 2026-04-25 — Cycle 10.C: Padrão 50 V1 retroactive audit (10m 18m janela contínua)

- nodes: P50-ST-14-3.0, P50-ST-14-3.5, P50-ST-20-3.5, P50-MA-20-50, P50-MA-25-75
- action: PADRAO_60_AUDIT_RETROACTIVE
- scripts: tools/v2_concat_10m_extended.py (3 datasets concat 18m), tools/v2_p50_10m_extended_audit.py
- result ma_crossover (6/6 ok): BTC Sh -2.27/-2.16, ETH Sh -0.85/-0.40, SOL Sh -1.44/-1.07. PnL -5 a -20% catastrófico.
- result supertrend (9 timeouts): mc-resamples=500 + 78k bars excede budget; mecanismo idêntico a MA → conservativ assumed GRAVEYARD
- decision: Padrão 50 GRAVEYARD coletivo confirmado após ciclos 1+5+7+10
- new_pattern: **Padrão 63** — trend-long 10m crypto catastrófico em janela longa (fees amplification + whipsaw)
- combined effect: Padrão 46 (MR 10m) + Padrão 63 (trend 10m) = TF 10m permanently graveyarded engine-only
- files: decisions/0225-v2-raio-cycle-10-padrao-50-graveyard-coletivo-padrao-63.md, GRAVEYARD.md, STATE.md
- next_node: Cycle 11 — implementar exit_layer engine (destrava 36 EX hipóteses V2) OU update AGENTS.md com guideline V2

## 2026-04-25 — Cycle 11.B: AGENTS.md V2 methodology guideline

- action: GUIDELINE_CONSOLIDATION
- result: AGENTS.md §9 adicionada com Padrões 53-63 + core gate AND-conjunto + lista falsificados + reaberturas + operational protocols + 6 methodology files pointers
- decision: methodology guideline V2 = leitura mandatória pra próximos agentes
- files: AGENTS.md
- next: Cycle 11.A

## 2026-04-25 — Cycle 11.A: Exit_layer MVP (TimeStopWrapper)

- action: ENGINE_NEW
- script: src/alpha_forge/strategies/exit_layer.py + edits em src/alpha_forge/cli/app.py
- result: TimeStopWrapper decorando qualquer Strategy; CLI flag --time-stop-bars N integrada (0=disabled, default); _build_strategy refatorado em base + wrapper conditional
- smoke test: bollinger 30/1.5 + filter + ts=12 BTC 30m → 125 trades 4 folds (vs ~150-200 baseline) ✓
- next: Cycle 11.C scout

## 2026-04-25 — Cycle 11.C: EX001 Scout (RAIO Nível 1)

- node: EX001 (Top 6 V2)
- action: SCOUT
- script: tools/v2_ex001_time_stop_scout.py
- jobs: 15 (3 assets × 5 variants raw/ts06/ts12/ts24/ts48); wall=23s
- result: 0/15 pass Padrão 60. Time stop curto prejudica (BTC ts06 Sh=-1.18, ETH ts06 Sh=-0.49); ts12 marginal SOL (+0.36 vs raw); ts24/48 ≈ raw (no-op).
- decision: EX001 → GRAVEYARD em Scout
- new_pattern: **Padrão 64** — EX001 time stop curto refutado para bollinger MR; signal natural mean-cross é mais limpo
- files: decisions/0226-v2-raio-cycle-11-exit-layer-mvp-ex001-graveyard-padrao-64.md, GRAVEYARD.md, AGENTS.md
- next_node: Cycle 12 — EX004 (ATR trailing) implementar wrapper similar OR LQ001/002 (liquidity_trap engine)

## 2026-04-25 — Cycle 12: ATRTrailingWrapper + EX004 Quarantined + Padrão 65

- action: ENGINE_NEW + SCOUT
- script: src/alpha_forge/strategies/exit_layer.py + tools/v2_ex004_atr_trail_scout.py
- jobs: 12 probes (3 assets × 4 variants raw/trail15/25/40); wall=26s
- result: 0/12 pass Padrão 60 strict; trail40 melhora Sh em todos 3 assets (BTC +0.24, ETH +0.24, SOL +0.37); SOL MDD reduce -5.2%
- decision: EX004 → QUARANTINED (direção validada, base sem edge). Padrão 65 registrado: ATR trail mult≥4.0 preserva winners + limita adverse.
- new_pattern: Padrão 65 — vol-aware exit > count-based exit em MR
- files: decisions/0227-v2-raio-cycle-12-atr-trailing-wrapper-ex004-padrao-65.md
- next: Cycle 13

## 2026-04-25 — Cycle 13: S12 + trail40 = Padrão 66 (primeira melhoria mensurável V2)

- action: APPLY_EX004_TO_SURVIVOR
- script: tools/v2_s12_atr_trail_combined.py
- jobs: 12 probes (3 assets × 4 variants); wall=186s
- result SOL: raw Sh=1.20 → trail40 Sh=1.37 (+14%), MDD 9.04→8.59 (-5%), PnL +29.2→+31.6 (+2.4pp). All 3 metrics improve.
- result BTC/ETH: continue FAIL (Padrão 62 confirmed — S12 SOL-microstructure)
- decision: S12+trail40 → PROMISING. EX004 trail40 → SCOUTING+ (validado em strategy real).
- new_pattern: **Padrão 66** — ATR trail40 + edge real = +14% Sh + MDD reduce; primeira melhoria mensurável V2/RAIO sobre survivor.
- gate gap: Sh 1.37 < 1.5 V1 strict; precisa +0.13 adicional para promotion (ou ADR de gate-relax)
- files: decisions/0228-v2-raio-cycle-13-s12-trail40-padrao-66-first-improvement.md, HYPOTHESIS_TREE.md
- next_node: Cycle 14 — EX009 BE-after-MFE wrapper + cumulative S12+trail40+BE pra empurrar Sh sobre 1.5

## 2026-04-25 — Cycle 14: BEAfterMFEWrapper + EX009 GRAVEYARD em S12 + Padrão 67

- action: ENGINE_NEW + SCOUT + CUMULATIVE
- script: src/alpha_forge/strategies/exit_layer.py + tools/v2_ex009_be_scout_combined.py
- jobs: 17 (12 standalone + 5 cumulative SOL); wall=215s
- result standalone S12+BE SOL: raw Sh=1.20 → BE05=0.68, BE10=0.64, BE15=0.78 (todos piores)
- result cumulative S12+trail40+BE SOL: cum_t40 Sh=1.37 → +BE05=0.81, +BE10=0.78, +BE15=0.93 (BE destrói gain)
- decision: EX009 → GRAVEYARD para S12 family (e provavelmente MR crypto alta-vol)
- new_pattern: **Padrão 67** — BE-after-MFE em short MR crypto alta-vol é stop too tight; preço retraça to entry intra-reversal forcing premature exit. Trail40 dominante.
- S12+trail40 (Sh=1.37) mantém best V2/RAIO survivor + enhancement
- files: decisions/0229-v2-raio-cycle-14-be-after-mfe-graveyard-padrao-67.md, GRAVEYARD.md
- next_node: Cycle 15 — Sensitivity grid S12 params (rsi_period × thresholds × trend_htf sma) pra empurrar Sh sobre 1.5

## 2026-04-25 — Cycle 15: S12 Sensitivity grid → Padrão 68 single-point optimum

- node: S12+trail40 sensitivity (RAIO Nível 3)
- action: SENSITIVITY_TEST (RAIO §4 Nível 3)
- script: tools/v2_s12_sensitivity_grid.py
- jobs: 27 (3 RSI periods × 3 thresholds × 3 trend_htf SMA), SOL 30m + trail40 + fees 10bps; wall=355s
- result: 1/27 pass Padrão 60 (canonical only); 0/27 pass V1 strict
- distribution: 9/27 Sh<0; 17/27 Sh<0.5; 26/27 Sh<1.0; 1/27 Sh=1.37 (canonical)
- decision: S12+trail40 → DOWNGRADE de PROMISING para QUARANTINED com Padrão 68 flag
- new_pattern: **Padrão 68 (CRÍTICO)** — Crystallized V1 hipóteses podem sobreviver janela longa mas falhar Sensitivity Test V2 Nível 3. Single-point optima são endemic em V1 selection. Gate V2 reformulado deve incluir Sensitivity ≥75% pass como gate adicional.
- methodology guideline V2 atualizada: agora 9 critérios AND-conjunto incluindo Sensitivity threshold
- after 15 cycles V2/RAIO: 0 strategies fresh promovíveis
- files: decisions/0230-v2-raio-cycle-15-s12-sensitivity-fail-padrao-68.md, HYPOTHESIS_TREE.md
- next_node: Cycle 16 — implementar liquidity_trap engine (LQ001/LQ002 — fundamentalmente novo, único caminho genuíno)

## 2026-04-25 — Cycle 16: LiquidityTrapStrategy engine + LQ001/002 GRAVEYARD + Padrão 69

- action: ENGINE_NEW (5o engine V2: LiquidityTrapStrategy)
- script: src/alpha_forge/strategies/families/liquidity_trap/strategy.py + tools/v2_lq_scout.py
- jobs: 18 probes (3 assets × 3 lookbacks × 2 variants); wall=26s
- result: 0/18 pass Padrão 60. BTC Sh -1.42 a -3.47, ETH similar, SOL menos pior (+0.17 melhor case mas MDD 22%).
- trade count 640-1130 → fees ~10% drag elimina edge
- decision: LQ001/002 naive → GRAVEYARD; engine preservado como base p/ variants filtradas
- new_pattern: **Padrão 69** — Microstructure naive sem filter (volume/wick/HTF context) destrói edge via fees. Implementação válida exige features adicionais (LQ005 wick mag, LQ006 volume, LQ011 mag+vol, LQ027 HTF align)
- after 16 ciclos V2: 0 strategies fresh promoted; pipeline rigoroso continua filtrando
- files: decisions/0231-v2-raio-cycle-16-liquidity-trap-engine-graveyard-padrao-69.md, GRAVEYARD.md
- next_node: Cycle 17 — adicionar wick magnitude filter à LiquidityTrapStrategy (LQ005) OU ADR de gate-relax discussion
