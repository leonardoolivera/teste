# 0218 — V2/RAIO Ciclo 4 — PF024 Add-one P52 PASS + P52 promovido Nível 6 (Candidate for ADR)

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13
**Relates to:** ADR-0217 (P52 SURVIVOR Cycle 3), ADR-0211/0214 (P52 historical), ADR-0030 (export gates)

## Contexto

Cycle 3 promoveu P52 BTC 18/60 a SURVIVOR (Replication + Sensitivity + Fee stress + Block bootstrap). Cycle 4 atacou Nível 5 Portfolio Integration via PF024 (Add-one candidate vs stack 13) — hipótese: P52 add deve melhorar portfolio sem aumentar MDD, ou queda gracefulmente em correlation cap.

Implementação: rodou os 13 combos do stack canonical + P52 BTC 18/60 sobre janela comum 2024-H2 (cada combo no seu asset original mas window=2024-H2 pra alignment temporal). 14 runs em 21s wall-clock. Equity curves alinhadas em 3456 bars.

## Resultado

| Métrica | A) Stack 13 | B) Stack 14 (+P52) | C) P52 standalone | Δ (B−A) |
|---|---:|---:|---:|---:|
| Sharpe | 0.5699 | **0.9063** | 3.0236 | **+0.3364** |
| Calmar | 0.6383 | **1.1942** | 10.3557 | **+0.5559** |
| MDD % | 4.4592 | **3.5548** | 2.2909 | **−0.9044** |
| PnL % | 1.1134 | 1.6537 | 8.7613 | +0.5403 |

**Sharpe melhora +60%; Calmar +87%; MDD reduz 20%; PnL +49%.** Todos os 4 eixos melhoram. PF024 PASS.

### Correlações P52 vs cada combo

| Combo | Correlação | Interpretação |
|---|---:|---|
| S10 (RSI short BTC 2025-H2) | -0.602 | hedge forte |
| S13 (RSI short width BTC 2025-H1) | -0.380 | hedge moderado |
| S06 (Bollinger short BTC 2025-H1) | -0.281 | hedge fraco |
| S11 (RSI short SOL 2025-H2) | -0.266 | hedge fraco |
| S04 (Bollinger long SOL 2024-H2) | +0.186 | descorrelacionado |
| Outros | -0.10 a +0.11 | descorrelacionados |

Mediana absoluta = 0.13. **P52 é estrutural hedge do stack** — reduz exposure conjunta a regimes adversos para os shorts (S10/S13/S06/S11 são todos shorts; P52 é long trend-following).

## Decisão

1. **PF024 PASS — P52 add-one melhora portfolio em todos eixos.**
2. **P52 promovido SURVIVOR → Nível 6 (Candidate for ADR).** Pacote de evidência completo:
   - Replication 2/6 cross-era (Cycle 1 RB004): edge em BTC + SOL 2024-H2.
   - Sensitivity 100% Sh ≥ 0.94 em 48 vizinhos (Cycle 2 RB012).
   - Fee resistance 2/2 fees 2x/3x (Cycle 1 RB007).
   - Block bootstrap 8/48 STRONG (Cycle 3 RB006); BTC 18/60 CI95=[0.04, 5.94].
   - Portfolio integration PF024 PASS (este ADR).
3. **MAS — ainda não-exportável para BotBinance.** Restrição ADR-0030/0203: cross-era além do regime de discovery é gate obrigatório. P52 é regime-2024-H2 dependente; testes em 2025-H1, 2025-H2 falham (Cycle 1 RB004 mostrou 0/4 fora de 2024-H2 e 2024-H1 não foi testado).

## Pré-condições para handoff BotBinance (futuro)

P52 não pode export até:
1. **Cross-era validation 2024-H1**: testar BTC ma_crossover 18/60 long-only em ETH/BTC/SOL 2024-H1. Dataset disponível.
2. **Cross-era validation 2023-H2**: idem em 2023-H2 (dataset disponível).
3. **Cross-era validation 2022-H1/H2** se disponível: BTC bear extreme + recovery.
4. Em pelo menos 1 era além de 2024-H2 deve manter Sh ≥ 1.0 com fees 10bps.
5. Manifest v3 schema com `runtime_contract: faithful` + invariantes ADR-0030.
6. ADR dedicado de approval (ADR-0219+) com rationale completo.

## Próximo Cycle 5 follow-ups

- **Cross-era 2024-H1 + 2023-H2 P52** (bloco de validação final pré-handoff). 12 probes (3 assets × 2 windows × 2 fee levels). ~3min wall-clock.
- **S10 fee resistance retest com bootstrap** (deferido de Cycle 2).
- **Re-evaluation outros nós da árvore**: implementar exit_layer, sizing_layer ou liquidity_trap engines pra atacar EX001/PS003/LQ001 (Top 20 V2) — esses são o backlog principal.

## Patterns updated

- **Padrão 52** (ma_crossover 20/50 — agora canonical 18/60): SURVIVOR + Candidate for ADR. Demonstrado: edge isolado + diversificação real do stack via correlações negativas.
- **Padrão 57 (novo):** P52 confirma que **trend-following long-only é hedge estrutural para stack majoritariamente short/MR em crypto 2024-H2**. Mecanismo causal: stack shorts perdem em rallies; P52 (trend-long) ganha em rallies. Diversificação por direcionalidade, não por engine.

## Consequences

- **Positive:** Primeiro candidato V2/RAIO completo a Nível 6. Pipeline RAIO entrega resultado pronto pra ADR de promoção. P52 demonstrou edge ISOLADO + valor PORTFOLIO simultâneamente — combinação rara.
- **Negative:** Cross-era além 2024-H2 ainda não testada — gate hard pré-export. Cycle 5 obrigatório antes de qualquer handoff BotBinance. P52 standalone tem MDD baixo (2.29%) mas window curta (6 meses); paper-trading prolongado também desejável.
- **Neutral:** Stack 13 atual continua canonical para handoffs em produção — adicionar P52 ao stack canonical exigiria ADR formal de "Stack v9".

## Não-alvo

- Não promover P52 a manifest sem cross-era 2024-H1/2023-H2 (gate ADR-0030).
- Não substituir o stack 13 atual por stack 14 com P52 sem ADR formal Stack v9.
- Não relaxar gate cross-era invocando "edge é forte demais" — disciplina V2 mantida.
- Não export P52 SOL configs (todas MARGINAL no bootstrap, fora da família STRONG BTC).

## Padrões totais: 57

- 52: P52 ma_crossover 18/60 — SURVIVOR + Candidate for ADR.
- 53-56: lições metodológicas do pipeline (fees floor, DSR limitação, script audit, block bootstrap).
- **57: trend-following long-only como hedge estrutural para stack short/MR cripto 2024-H2.**
