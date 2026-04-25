# SEARCH_STATE

**Updated:** 2026-04-25
**Protocol:** LIGHTNING_SEARCH_PROTOCOL.md (RAIO §11)

```yaml
current_node: P52-Q-001 (PROMISING — pending Sensitivity Test)
current_branch: Padrão 52 ma_crossover 20/50 regime-2024-H2 cross-asset
best_open_nodes:
  - node_id: P52-Q-001
    priority_score: 8.2
    reason: Único survivor Cycle 1 — promising; cross-era 2/6 BTC+SOL 2024-H2, fee resistant
  - node_id: P51-002
    priority_score: 5.5
    reason: Quarantined prior reduzido — fee resistant ETH 2024-H2, mas single-window
best_survivors:
  - node_id: RB-ROOT-018
    level: 4
    reason: 658/658 V1 runs clean; ADR-0030 invariants ok
best_quarantined:
  - node_id: P51-002
    reason: bollinger 17/2.0 ETH 2024-H2 fee resistant; precisa Sensitivity para escapar quarentena
recently_rejected:
  - node_id: P50-Q-001 (cross-engine cluster)
    reason: GRAVEYARD per ADR-0214 — fee stress 0/10 fatal
  - node_id: P51-001
    reason: GRAVEYARD — cross-era 1/6 SOL-only re-detection P48
  - node_id: P51-003
    reason: GRAVEYARD — mesmo perfil P51-001
compute_budget_used: 76 unidades (4 audit + 72 RB004+RB007)
compute_budget_remaining: TBD
next_action: |
  1. ADR-0215: RB007 fee stress sobre 13 stack canonical manifests (auditoria fee fragility análoga ao P50)
  2. Sensitivity Test P52-001 (RAIO Nível 3): ma_crossover (18/45, 18/55, 22/45, 22/55) × (BTC, ETH, SOL × 2024-H2) = 12 probes
  3. DSR/PSR P52 family (precisa scipy/numpy)
last_decision: 2026-04-25 ADR-0214 — Padrão 50 GRAVEYARD, 51 majoritariamente GRAVEYARD, 52 PROMISING
blocked_items:
  - item: EX-ROOT-001..036 (36 hipóteses Exit Research)
    reason: Engine exit_layer ausente; ADR de implementação pendente
  - item: PS-ROOT-001..027 (27 hipóteses Position Sizing)
    reason: ADR-0030 invariants forbid non-fixed_notional sizing in production; pesquisa permitida com sizing_layer engine + ADR
  - item: LQ-ROOT-001..027 (27 hipóteses Liquidity Trap)
    reason: Engine liquidity_trap ausente; alguns precisam orderbook
  - item: RM-ROOT-001..012, 014..036 (35 hipóteses Regime Meta)
    reason: regime_meta engine ausente; subset precisa multi-asset alignment + funding/volume
  - item: PF-ROOT-002..022, 024..027 (25 hipóteses Portfolio)
    reason: Lib estatística (numpy/scipy risk parity, min variance, correlation cap) ausente
  - item: XP-ROOT-001..009 (9 hipóteses Exploratory)
    reason: Dados externos ou ML pipeline
updated_at: 2026-04-25
```
