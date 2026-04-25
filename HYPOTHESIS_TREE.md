# HYPOTHESIS_TREE

**Updated:** 2026-04-25
**Protocol:** LIGHTNING_SEARCH_PROTOCOL.md (RAIO)
**Roadmap base:** ROADMAP_ESTRATEGIAS_V2_METODOLOGICO.md
**Adoption ADR:** [0213](decisions/0213-v2-raio-adoption-prereg.md)

> Estado vivo da árvore de pesquisa. Cada nó segue o schema RAIO §3. Status: CANDIDATE | SCOUTING | PROMISING | EXPAND | PAUSED | QUARANTINED | REJECTED | SURVIVOR | VALIDATED | GRAVEYARD.

---

## Roots (raízes)

Raízes ativas do roadmap V2. Cada raiz pode gerar até 3 filhos iniciais (RAIO §5).

| node_id | root_family | tier | hypothesis | status | level | priority_score | next_step |
|---|---|---|---|---|---:|---:|---|
| RB-ROOT-018 | Robustness | T5 | Execution invariant audit cobre todos os 658 V1 runs | **SURVIVOR** | 4 (audit) | 7.8 | done — 658/658 clean |
| PF-ROOT-001 | Portfolio Stack | T4 | Equal weight stack 13 é benchmark formal | **QUARANTINED** | 0 | 7.6 | Aguarda infra de equity-curve aggregation alinhada por timestamp |
| PF-ROOT-023 | Portfolio Stack | T4 | Ablation one-combo-out mede dependência | **QUARANTINED** | 0 | 7.3 | Mesmo bloqueio de PF-ROOT-001 |
| RM-ROOT-013 | Regime Meta Gating | T3 | BTC risk-off gate protege alt longs | **PAUSED** | 0 | 5.7 | Engine novo: `CrossAssetReturnFilter` em `regimes/filter.py` |
| **V2-RB004-007** | Robustness | T5 | Cross-era + fee stress sobre V1 winners | **SCOUTING** | 2-4 | 7.5 | Running: 72 probes (9 configs × 6 cross-era + 2 fee stress) |

### V1 inheritance status (post-Cycle 1, ADR-0214)

| node_id | from_v1 | hypothesis | status (post-Cycle 1) | next_step |
|---|---|---|---|---|
| P50-Q-001 | Padrão 50 | Bear-avoidance trend ETH 2025-H1 cross-engine | **GRAVEYARD** | enterrado: cross-era 2/30 + fee stress 0/10. Era artefato fees-low + single-window. |
| P51-001 | Padrão 51a | bollinger 15/2.0 ETH 2024-H2 | **GRAVEYARD** | cross-era 1/6 (SOL 2024-H2 = P48 re-detection). |
| P51-002 | Padrão 51b | bollinger 17/2.0 ETH 2024-H2 | **QUARANTINED (prior reduzido)** | Único survivor parcial: fee stress 2/2 ETH 2024-H2. Próximo: Sensitivity Test perturbação local. |
| P51-003 | Padrão 51c | bollinger 15/1.75 ETH 2024-H2 | **GRAVEYARD** | mesmo perfil P51-001. |
| **P52-Q-001** | Padrão 52 (canonical 18/60) | ma_crossover BTC 18/60 long-only | **GRAVEYARD (Cycle 7)** | Janela contínua 30 meses: Sh ≤ 0.87 todas configs. Edge intra-2024-H2 era selection bias temporal. bh_drawdown(15%) reduz MDD ~60% mas Sh insuficiente para gate. ADR-0221. |

### Stack 13 audit Padrão 60 (Cycle 8 retroativo) — adicionado 2026-04-25

| node_id | combo | result | status | next |
|---|---|---|---|---|
| S12-survivor | rsi_short_trendhtf SOL 2025-H1 | Sh=1.20 30m, PnL +29%, único ROBUST do stack | **SURVIVOR** | Cycle 9: cross-asset FAIL (SOL-only). Cycle 13: + trail40 → Sh=1.37 (+14%), MDD=8.59 (-5%), PnL=+31.6% (Padrão 66) |
| S12+trail40 | S12 + EX004 ATR trail (atr14, mult4.0) | Sh=1.37 SOL 30m (canonical only); **Sensitivity 1/27 pass** | **QUARANTINED Padrão 68** | Single-point optimum confirmado. Vizinhança paramétrica hostile (96% FAIL Padrão 60). Não promove sem evidência adicional ou ADR de gate-relax + paper-trade extended. |
| EX001-time-stop-MR | bollinger MR + time stop ts06/12/24/48 | 0/15 pass Padrão 60 (Cycle 11) | **GRAVEYARD** | Padrão 64: signal natural mean-cross é exit mais limpo |
| EX004-atr-trail | bollinger MR + atr trail40 | 0/12 pass Padrão 60 mas Sh +0.24-0.37 todos (Cycle 12); aplicado a S12 funciona (Cycle 13) | **SCOUTING+** | Padrão 65+66: trail40 boost edge real +14% Sh; aplicar a próximos survivors |
| S01-S02-S03-marginal | bollinger_width_regime_v2 long-only ETH/BTC | Sh 0.62-0.89 30m | MARGINAL | Não promove sem Sh > 1.0; manter em stack mas reconhecer fragilidade |
| S10-S11-graveyard-candidate | rsi_short_pure_2025h2 BTC + SOL | Sh -0.58/-0.38 30m, MDD 22-36% | **GRAVEYARD CANDIDATE** | Paper-trade observation extended antes de retirada definitiva |
| S04-S08-S13-fail | bollinger short variants + rsi_short_width | Sh < 0.5, Padrão 60 FAIL | FAIL stack-only | Manter como diversificação se correlação amortece; Sh standalone insuficiente |

### Backlog roots (deferred — dependências de engine novo)

| node_id | family | reason_paused | unblock_condition |
|---|---|---|---|
| EX-ROOT-001..036 | Exit Research | Engine `exit_layer` não existe na CLI | Implementar exit_layer (time stop, ATR trail, BE, MFE/MAE filters) |
| PS-ROOT-001..027 | Position Sizing | Engine `sizing_layer` ausente; ADR-0030 invariantes | ADR-0214+ permitindo sizing layer; manifests v3 só aceitam fixed_notional |
| LQ-ROOT-001..027 | Liquidity Trap | Engine `liquidity_trap` ausente; OHLCV-proxy precisa scaffold | Implementar break/sweep/wick rejection detector |
| RM-ROOT-001..036 | Regime Meta Gating | Maioria requer regime_meta engine ou dados extras (funding/multi-asset) | Implementar regime_meta + ingest se aplicável |
| PF-ROOT-002..022, 024..027 | Portfolio Stack | Risk parity, min variance, correlation cap, drawdown-aware: lib estatística nova | Implementar portfolio.py com numpy/scipy |
| XP-ROOT-001..009 | Exploratory | Dados externos (funding, orderbook, options, liquidations) ou ML pipeline | Ingest dedicado por XP, ADR antes de producao |

---

## Tree (filhos por raiz)

> Vazio inicialmente. À medida que Scouts (Nível 1) rodarem, filhos vão sendo registrados aqui per RAIO §5.

### RB-ROOT-018 — Execution invariant audit

(sem filhos ainda — raiz pendente Scout)

### PF-ROOT-001 — Equal weight stack 13 benchmark

(sem filhos ainda)

### PF-ROOT-023 — Ablation one-combo-out

(sem filhos ainda)

### RM-ROOT-013 — BTC risk-off gate

(sem filhos ainda)

---

## Compute budget tracker (RAIO §9)

| Allocation | Used | Total | Remaining |
|---|---:|---:|---:|
| Promising/Expand (60%) | 0 | TBD | TBD |
| New roots (20%) | 0 | TBD | TBD |
| Falsification survivors (10%) | 0 | TBD | TBD |
| Quarantined (10%) | 0 | TBD | TBD |
| **Total** | **0** | **TBD** | **TBD** |

Budget unitário: 1 unidade ≈ 1 backtest no dispatcher V1 (~6-30s wall-clock).
