# 0219 — V2/RAIO Ciclo 5 — P52 cross-era FALHA + downgrade Candidate→Quarantined regime-conditional

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13
**Relates to:** ADR-0218 (Cycle 4 PF024 PASS), ADR-0217 (P52 SURVIVOR), ADR-0030 (export gates)

## Contexto

ADR-0218 promoveu P52 BTC 18/60 a "Candidate for ADR (Nível 6)" após PF024 PASS — porém condicionou export BotBinance a cross-era validation além do regime de discovery (2024-H2). Cycle 5 executou esse gate.

Tools: [`tools/v2_rb004_p52_cross_era_gate.py`](../tools/v2_rb004_p52_cross_era_gate.py). 24 probes (3 assets × 4 windows × 2 fee levels) em 11s wall-clock.

## Resultados (fees 10bps default V2 screening)

| Window | BTC | ETH | SOL | Pass count |
|---|---:|---:|---:|---:|
| 2022-H1 | -2.61 | -1.57 | -0.10 | **0/3** (bear extreme: LUNA crash) |
| 2022-H2 | -2.85 | -2.18 | -2.85 | **0/3** (bear: FTX collapse) |
| 2023-H2 | 0.67 | -0.30 | **+3.46** | 1/3 |
| 2024-H1 | 0.11 | 0.72 | 1.44 (tr=27 < 30) | **0/3** |

**Total: 1/12 probes passa gate** (SOL 2023-H2 Sh=3.46).

### Gate ADR-0030 (cross-era ≥ 2 windows × ≥ 2 assets)

- Windows com ≥ 2 assets passando: **0** de 4 testadas.
- **Gate ADR-0030: FAIL.**

### Análise por regime

- **Bear extreme (2022 H1+H2):** P52 catastrófico em todos 3 assets, todos fees. Drawdown 6-12% por probe. Trend-following long-only **explode** em bear absoluto — entra em fakes rallies pré-continuação queda. **Edge negativo, não neutro.**
- **Recovery early (2023-H2):** mixed. SOL ressuscita agressivo (+3.46), BTC marginal (+0.67), ETH ainda bear-marked (-0.30). Único window não-2024 com qualquer pass.
- **Pre-discovery (2024-H1):** margin-positive em todos 3 mas nenhum atinge gate (Sh 0.11-1.44; SOL trade count abaixo de 30).
- **Discovery (2024-H2 — não testado novamente neste ADR, mas conforme ADR-0217):** STRONG em BTC; outros marginal.

## Decisão

1. **P52 NÃO passa gate ADR-0030 cross-era.** Edge é regime-2024-H2 dependente confirmado, com extensão fraca em recovery 2023-H2 (apenas SOL).
2. **Downgrade RAIO:** P52-Q-001 de "Candidate for ADR (Nível 6)" → **"QUARANTINED com escopo regime-2024 only"**. Mantém SURVIVOR status histórico (passou Replication, Sensitivity, Fee stress, Block bootstrap, Portfolio Integration intra-window) mas falha gate cross-era.
3. **NÃO export para BotBinance** sem regime detector que bloqueie execução em bear (2022-style). Sem regime detector, P52 deployado em produção causaria drawdown >>10% no próximo bear extreme.
4. **Padrão 58 (novo):** trend-following long-only em crypto é **regime-conditional**, não all-weather. Funciona em bull/recovery (2024-H2 +35%, SOL 2023-H2 +25%); explode em bear absoluto (2022-H1/H2: -6 a -12%). **Não pode ser deployado standalone sem regime gate.**
5. P52 retorna ao backlog como input pra hipóteses **regime + P52 conjunto** (RM013 BTC risk-off gate alt longs; RM017 risk-off tri-asset bear-avoidance; RM034 B&H DD > 35% gate).

## Lessons (ciclo + meta-padrão)

- **Padrão 58 (regime-conditional):** trend-following long-only crypto é hedge SOMENTE em bull/recovery. Em bear, é amplificador de drawdown. PF024 PASS de Ciclo 4 era específico ao regime 2024-H2; em bear 2022, P52 + stack 13 teria drawdown *pior* que stack sozinho (P52 long em mercado de queda + shorts já short).
- **Lição ADR-0218 retroativa:** PF024 PASS isolado não é gate suficiente — Portfolio Integration **dentro do regime de discovery** sempre é mais favorável que cross-era. Próximos PF024 devem ser executados em ≥ 2 regimes distintos.
- **Adoção V2:** novos candidatos a Nível 5 PF024 devem rodar PF024 em pelo menos 2 windows distintas antes de promoção a Nível 6.

## Consequences

- **Positive:** Pipeline RAIO entregou exatamente o que foi projetado pra entregar — capturou um falso positivo (PF024 PASS regime-specific) ANTES de virar manifest. V1 teria promovido após PF024 PASS, sem esse gate.
- **Negative:** Após 5 ciclos RAIO + 6 ADRs (0212-0219), zero strategy V2/RAIO promovida a manifest. Pipeline rigoroso = baixa taxa de promoção. Esperado per V2 metodológico.
- **Neutral:** Templates V2 (HYPOTHESIS_TREE, NODE_LOG, GRAVEYARD, SEARCH_STATE) consolidados como infra padrão de pesquisa.

## Próximas frentes

Per RAIO §13 (anti-pergunta), próximas ações ranqueadas por priority_score:

1. **Implementar regime detector** (RM013 BTC risk-off OR RM034 B&H DD gate) que bloqueie P52 em bear. Engine novo: `CrossAssetReturnFilter` ou `BHDrawdownFilter`. Custo dev: médio. Após implementado, retestar P52 + regime gate cross-era. Score ~7.0.
2. **Implementar exit_layer** (EX001 time stop curto MR, EX004 ATR trailing, EX009 BE after MFE — Top 6/9/8 do V2). Engine novo: significativo. Score ~7.5 (EX001).
3. **Implementar liquidity_trap** (LQ001/LQ002 Top 18-19 V2). Engine novo. Score ~7.0.
4. **PF024 retest em 2024-H1 + 2023-H2** (não P52 — outros candidatos). Esperar até ter survivor pós-Cycle 5.
5. **Backlog cleanup**: mover hipóteses paused em SEARCH_STATE.

Recomendação autopilot: **implementar exit_layer** (EX001) — Top 6 V2, atinge gap mais óbvio do roadmap V1, e exit research é o que tem mais probabilidade de gerar candidatos novos (V1 testou apenas signal exits). Custo dev ~3-5h estimado, mas destrava 36 hipóteses EX*.

## Patterns updated

- **Padrão 52:** downgrade de Candidate-for-ADR → Quarantined regime-2024 only. Não export até implementar regime detector + retestar.
- **Padrão 58 (novo):** trend-following long-only crypto é regime-conditional (bull/recovery only); explode em bear absoluto. Standalone sem regime gate é proibido em produção.

## Não-alvo

- Não export P52 standalone para BotBinance (gate ADR-0030 explicitly FAIL).
- Não tentar variações P52 cross-era pra "salvar" — Padrão 58 é claro.
- Não promover P52 + naive regime gate (e.g. SMA cross) sem testar formalmente.
- Não desistir de P52 — está em Quarantined, pode reabrir com regime detector validado.

## Padrões totais: 58
