# 0213 — V2 + PROTOCOLO RAIO adoption — pre-reg

**Status:** Proposed (pre-reg)
**Date:** 2026-04-25
**Deciders:** Usuário ("ok, confirmo" o pivot), agente
**Relates to:** ADR-0212 (V1 closeout), `ROADMAP_ESTRATEGIAS_V2_METODOLOGICO.md`, `LIGHTNING_SEARCH_PROTOCOL.md`

## Contexto

V1 fechado em ADR-0212 com 658/1000 runnable cobertos. Crítica metodológica registrada: produto cartesiano, single-window outliers, zero correção data-snooping formal, lacunas em Exit/Sizing/Portfolio/Liquidity/Robustness.

V2 (`ROADMAP_ESTRATEGIAS_V2_METODOLOGICO.md`) propõe 180 hipóteses falsificáveis com mecanismo causal explícito em 7 famílias. RAIO (`LIGHTNING_SEARCH_PROTOCOL.md`) define **árvore adaptativa** com 7 níveis (Idea → Scout → Replication → Sensitivity → Robustness → Portfolio → ADR), backtracking obrigatório, score de priorização, budget progressivo, regras anti-pergunta e anti-data-snooping.

## Decision

Adotar **V2 como roadmap de pesquisa** e **RAIO como protocolo de execução**. Encerra a era de batches paralelos cobertura-completa do V1; inicia era de árvore adaptativa.

### Estrutura operacional adotada

1. **HYPOTHESIS_TREE.md** = árvore viva (raízes + branches por status, level, score).
2. **NODE_LOG.md** = diário append-only de cada teste.
3. **SURVIVORS.md** = nós Nível 4+ com evidência consolidada.
4. **GRAVEYARD.md** = nós cortados; impede repetição.
5. **SEARCH_STATE.md** = estado operacional atual + best_open_nodes + budget.
6. **EXPANSION_RULES.md** = regras de geração de filhos (3/5/8 limit por status).
7. **VALIDATION_LADDER.md** = referência detalhada dos 7 níveis.

### Reuso de infraestrutura V1

- `tools/run_roadmap_auto.py` (dispatcher 10-workers) → executor RAIO Nível 1 Scout + Nível 2 Replication. Adapter que aceita node_id como input em vez de roadmap_1000.json entry.
- `tools/audit_roadmap_auto_vs_batches.py` (cross-check) → padrão para todo audit RB018-style.
- `tools/summarize_roadmap_auto.py` → base do summarizer por família V2.
- 658 r1k-* runs preservados → input para PF023 (ablation), PF001 (equal weight benchmark), RB018 (execution invariant audit).

### Padrões V1 → quarantined nodes V2

Os 3 padrões do V1 (50, 51, 52) entram na árvore V2 como **Quarantined** (não Survivor), pelos critérios RAIO seção 6:
- "single-window outlier risk" + "promissor mas trade_count baixo em janela única" → Quarantined até passar Nível 2 Replication (cross-era).
- Não vão para Graveyard porque mecanismo causal segue plausível (regime bear-avoidance, regime flat short-window MR).
- Não viram Survivor porque V1 não passou validação Nível 4 (Monte Carlo, fee/slippage stress, DSR/PSR).

### Primeira fase RAIO-V2 (este ADR)

**Top 4 hipóteses V2 executáveis sem engine novo:**

| ID | Família | Hipótese | Engine V1 reaproveitável | Custo dev |
|---|---|---|---|---|
| RB018 | Robustness | Execution invariant audit | Lê `walk_forward.json` dos 658 r1k runs | Baixo (script de audit) |
| PF001 | Portfolio Stack | Equal weight stack 13 benchmark | Stack 13 manifest existe; precisa retorno equal-weight aligned | Baixo (script de aggregação) |
| PF023 | Portfolio Stack | Ablation one-combo-out | Stack 13 + leave-one-out | Baixo (loop sobre ablation) |
| RM013 | Regime Meta Gating | BTC risk-off gate alt longs | Adicionar `--regime-filter btc_return_24h:lt=0` no CLI ou wrapper externo | Médio (filtro novo + wrapper) |

**Hipóteses V2 deferidas (engine novo):** todas as 36 EX001-EX036 (exit_layer), 27 PS001-PS027 (sizing_layer), 27 LQ001-LQ027 (liquidity_trap), maior parte das RM*-RM036 (regime_meta novos), PF002-PF022 (portfolio com correlação/risk parity), 9 XP001-XP009 (exploratory), e a maioria das RB001-RB018 que precisem PSR/DSR/Reality Check (validação estatística nova).

### Score de priorização inicial

Aplicar formula RAIO seção 8:
```
priority_score =
  0.25 * edge_quality + 0.20 * robustness + 0.15 * causal_plausibility
+ 0.15 * portfolio_value + 0.10 * novelty + 0.10 * validation_need
- 0.15 * overfit_risk - 0.10 * compute_cost - 0.10 * implementation_complexity
```

Para Top 4:
- **RB018**: edge=N/A, robustness=N/A (audit), causal=10, portfolio=8 (fundação), novelty=10, validation_need=10, overfit=0, compute=1, complexity=2 → **score ~7.8**
- **PF001**: edge=N/A, robust=8, causal=10, portfolio=10, novelty=8, validation=9, overfit=2, compute=2, complexity=2 → **score ~7.6**
- **PF023**: edge=N/A, robust=8, causal=9, portfolio=10, novelty=7, validation=10, overfit=3, compute=3, complexity=2 → **score ~7.3**
- **RM013**: edge=6 (RM013 é Top 1 promissora V2), robust=N/A, causal=8, portfolio=7, novelty=7, validation=8, overfit=5, compute=3, complexity=4 → **score ~5.7**

Ordem de execução: **RB018 → PF001 → PF023 → RM013**. RB018 primeiro pq garante que os 658 V1 runs são causalmente válidos antes de PF001/PF023 dependerem deles.

### Budget alocado

Fase RAIO inicial usa budget RAIO-1: 4 hipóteses × Nível 1 Scout × 1 unidade = 4 unidades (~30 min compute estimado). Demais 176 hipóteses V2 ficam em backlog ranqueado.

### Stop conditions específicas

- Se RB018 detectar lookahead/fill violation em qualquer dos 658 V1 runs → **freeze de pivot até audit completo**, escrever ADR-0214 com escopo do bug, refazer wave afetada com fix.
- Se 2 das 4 Top hipóteses falharem Scout (Nível 1) → revisar premissas V2 antes de gerar Nível 2.
- User redirect → obedecer.

## Consequences

- **Positive:** árvore com state machine impede expansão cega; budget força priorização; cada teste tem registro pré-reg + critério invalidação; backtracking explícito em vez de "tentar de novo um pouquinho diferente"; falsificação estatística (DSR/PSR/Reality Check) entra como gate explícito; cobre lacunas V1 (Exit/Sizing/Portfolio/Liquidity).
- **Negative:** velocidade absoluta diminui (V1 fazia 200 backtests/min em paralelo; V2 faz 1 hipótese por vez com replication+sensitivity); requer dev de 5-6 engines novos ao longo do tempo (não tudo de uma vez per RAIO seção 9: 60% promising/expand, 20% exploration); curva de aprendizado dos templates auxiliares.
- **Neutral:** V1 dispatcher continua existindo como executor de Scout. 658 r1k-* runs preservados como input. Manifests aprovados (handoff BotBinance) intocados — V1 não tinha promovido nenhum manifest novo desde Wave 2.

## Alternatives considered

- **Aplicar V2 sem RAIO (linear).** Rejeitado: V2 sozinho é só lista de hipóteses melhor-estruturadas; sem RAIO repete o erro do V1 (executar tudo sequencialmente). RAIO é o que dá disciplina de árvore + budget + anti-pergunta.
- **Implementar todos os 7 templates auxiliares antes de qualquer Scout.** Rejeitado: RAIO é YAGNI-amigável. Materializar HYPOTHESIS_TREE + NODE_LOG + SEARCH_STATE primeiro (mínimo viável) e escalar conforme necessidade real.
- **Pular Top 4 e ir direto para EX001 (time stop curto MR — Top 6 V2).** Rejeitado: EX001 requer engine novo (exit_layer); Top 4 são auditoria/portfolio que validam o existente antes de construir o novo.

## Follow-ups

- Materializar templates auxiliares mínimos (HYPOTHESIS_TREE, NODE_LOG, SEARCH_STATE, GRAVEYARD).
- Carregar Padrões 50/51/52 como Quarantined nodes (P50-Q-001, P51-Q-001, P52-Q-001).
- Implementar RB018 (audit script) → run sobre 658 r1k runs.
- Implementar PF001 + PF023 (portfolio aggregation script).
- Implementar RM013 (CLI extension ou wrapper para `btc_risk_off` filter).
- STATE.md update com pivot V1→V2+RAIO.

## Não-alvo

- Não materializar todos 7 templates de uma vez se uso real não justifica.
- Não promover nenhum nó V2 a Survivor sem passar Nível 4 Robustness completo.
- Não export para BotBinance até ADR de manifest dedicada.
