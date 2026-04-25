# 0212 — Roadmap 1000 V1 closeout + pivot para V2+RAIO

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Usuário ("ok, confirmo" o pivot), agente
**Relates to:** ADR-0203 (roadmap 1000 V1), ADR-0209/0210/0211 (Fases auto-paralelas), ROADMAP_ESTRATEGIAS_V2_METODOLOGICO.md, LIGHTNING_SEARCH_PROTOCOL.md (PROTOCOLO RAIO)

## Contexto

Roadmap 1000 (ADR-0203) gerou backlog cartesiano de 1000 probes em 4 tiers. Execução automática paralela (ADR-0209/0210/0211) cobriu **658/1000 = 65.8% runnable** em 37min wall-clock total via dispatcher 10-workers (`tools/run_roadmap_auto.py`):
- Wave 1 (filter=none): 204 probes, 14 passes
- Wave 2 (with_filter+canonical+perturbações+ablações): 390 probes, 54 passes
- Wave 2b (donchian canonical fix): 64 probes, 0 passes (consistente com ADR-0202 — donchian morto cross-TF)

68 probes com gate duplo (Sh ≥ 1.5 ∧ trades ≥ 30 ∧ alfa > 0). 3 padrões registrados:
- **Padrão 50** (promovido cross-engine): bear-avoidance ETH 2025-H1, 5 configs supertrend/ma_crossover.
- **Padrão 51** (candidato): bollinger window=15-17 ETH 2024-H2 regime flat.
- **Padrão 52** (candidato): ma_crossover canonical 20/50 ETH 2024-H2 Sh=3.76 isolado.

Restantes 342/1000 **não são compute, são código**:
- regime_meta (45), portfolio_stack13 (36), portfolio_subset (14), stack_combo (70): engines compostos não-existentes na CLI.
- exotic_feature_flag (144), ml_feature_flag (1): T4, requerem ingest de dados novos (orderbook/funding/CVD) e pipeline ML.
- Filtros regime-detector novos (~75): atr_expansion_50pct, trend_htf_4h_sma50_flat, realized_vol_percentile_70, width_narrow_10m, funding_rate_extreme, ablation_no_width, ablation_no_trend_htf.
- Dataset gaps LINK/DOT/AVAX 2024-H2 (~12).
- Perturbações não-mapeáveis (`threshold ± 5` em bollinger, ~3).

## Decisão

**Encerrar formalmente o Roadmap 1000 V1 a 658/1000 cobertos.** Os 342 restantes são obsoletados pelo Roadmap V2 (`ROADMAP_ESTRATEGIAS_V2_METODOLOGICO.md`), que substitui produto cartesiano por **180 hipóteses falsificáveis** com mecanismo causal explícito, em 7 famílias (Regime/Exit/Sizing/Portfolio/Liquidity/Robustness/Exploratory).

**Pivot para V2 + PROTOCOLO RAIO.** ADR-0213 (separado) faz pre-reg da adoção. Este ADR documenta apenas o fechamento do V1.

## Crítica retrospectiva ao V1 (justificativa do pivot)

Aplicando os critérios V2 (seção 11 "Critérios de descarte rápido") aos achados V1:

1. **Padrão 50 cross-engine — single-window.** 5 configs passam gate em ETH 2025-H1, mas TODAS na mesma window. V1 promoveu a "validado cross-engine"; V2 categorizaria como **risco alto de single-window selection** sem cross-era validation.
2. **Padrão 51 short-bollinger — single-window.** ETH 2024-H2 apenas. Risco idêntico.
3. **Padrão 52 ma_crossover — single-probe.** 1 config, 1 window. Insuficiente.
4. **Duplicatas no top-23.** 8 dos 23 top probes são duplicatas (mesma config alcançada via 2 caminhos do roadmap: explicit `15/2.0` + perturbação `window *= 0.83 → 17 ≈ 15`). Inflação aparente do count.
5. **Zero correção data-snooping formal.** DSR/PSR/Reality Check ausentes. 658 testes correlacionados, alfas pequenos (3-8% pra maioria dos passes) — cauda da distribuição de Sharpe sob null hypothesis explica boa parte dos 68 passes.
6. **Gate alfa pós-hoc.** `BH_APPROX` table hardcoded em `summarize_roadmap_auto.py` — não é benchmark causal nem ajustado por leverage corretamente.
7. **Engines exits/sizing/portfolio/liquidity ausentes.** V1 testou apenas entry parameters. V2 identifica que isso é exatamente onde edges robustos costumam estar.

## Consequences

- **Positive:** roadmap V1 fechado com cobertura honesta (66% runnable, 0 falhas, infra preservada e auditável); padrões V1 não são descartados — viram **input quarantined nodes** no RAIO V2 (Nível 2-3 entry, prontos pra Robustness validation); V2 ataca lacunas reais (Exit/Sizing/Portfolio/Liquidity/Robustness estatística); RAIO impede expansão cega via score+budget+anti-data-snooping; dispatcher V1 (`tools/run_roadmap_auto.py`) reutilizado como executor RAIO Nível 1 Scout + Nível 2 Replication.
- **Negative:** trabalho de implementação dos 5-6 engines novos (regime_meta, exit_layer, sizing_layer, portfolio, liquidity_trap, ensemble) que estavam no V1 ainda precisa ser feito — agora sob escopo V2 com mecanismo causal pré-declarado, em vez de produto cartesiano; padrões V1 perdem status "promovido"/"candidato" e voltam para "Quarantined nodes" do RAIO até passarem cross-era validation.
- **Neutral:** 658 r1k-* run-dirs preservados em `results/validation/`; `roadmap_auto_progress.json` continua canônico do V1; futuros backtests V2 produzem run-ids com prefixo distinto (e.g. `v2-RM013-...`) pra evitar colisão.

## Alternatives considered

- **Implementar os 5 engines V1 e fechar 1000/1000.** Rejeitado: ~30-50h dev, gera mais 290+ probes correlacionadas com mesmas falhas metodológicas. V2 categoriza essas mesmas hipóteses sob mecanismo causal melhor.
- **Continuar V1 e rodar V2 em paralelo.** Rejeitado: confunde escopo, duplica trabalho, e V2/RAIO explicitamente substituem V1 (seção 2 do roadmap V2).
- **Ignorar V2 e seguir só com cross-era validation dos Padrões 50/51/52.** Rejeitado: validação cross-era é apenas Nível 4 do RAIO; faz mais sentido fazê-la dentro do framework V2 que já estrutura outros níveis.

## Follow-ups

- ADR-0213: pre-reg V2+RAIO adoption.
- Materializar templates: HYPOTHESIS_TREE.md, NODE_LOG.md, GRAVEYARD.md, SEARCH_STATE.md, SURVIVORS.md, EXPANSION_RULES.md, VALIDATION_LADDER.md.
- Carregar Padrões 50/51/52 como Quarantined nodes em HYPOTHESIS_TREE.
- Top 4 V2 atacáveis sem engine novo: RB018, PF001, PF023, RM013.
- STATE.md update com pivot.

## Não-alvo

- Não promover nenhum padrão V1 a manifest sem passar pelo V2/RAIO (cross-era + DSR/PSR + Robustness Nível 4).
- Não rodar dispatcher V1 com novos batches (V1 está fechado; futuros runs vão para árvore V2).
- Não modificar `decisions/roadmap_1000.md` retroativamente — fica como documento histórico.
