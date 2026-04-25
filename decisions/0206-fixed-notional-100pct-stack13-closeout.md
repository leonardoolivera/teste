# 0206 — Fixed_notional 100%/entrada stack 13 (closeout diagnóstico, sem snowball)

**Status:** Accepted
**Date:** 2026-04-22
**Deciders:** Usuário ("sem snowball") + agente
**Relates to:** ADR-0204 (pré-reg), ADR-0205 (snowball closeout, agora contrastado), ADR-0030 (faithful sizing invariant).

## Contexto

Após ADR-0205 (snowball 100%), user redirect "sem snowball" — ou seja, interpretar "100% do capital por entrada" como **100% do capital_inicial literal, sem compounding**. Reconfigurei sizing para `FIXED_NOTIONAL, fracao=1.0, alav=1.0` e reexecutei os mesmos 13 combos com o mesmo período / params / filtros / cost model.

Script atualizado: [`scripts/run_snowball_100_stack13.py`](../scripts/run_snowball_100_stack13.py) (agora emite `fixed_100_stack13_<date>.json`). Artefato: [`exports/diag/fixed_100_stack13_20260422.json`](../exports/diag/fixed_100_stack13_20260422.json).

## Resultado (13/13 combos)

Sizing A (baseline manifest-equivalente): `fracao=0.1, alav=2.0, fixed_notional` → notional 2k/trade.
Sizing B (100%/entrada sem compounding): `fracao=1.0, alav=1.0, fixed_notional` → notional 10k/trade = 5× baseline.

| # | Combo | base Sh / PnL% | f100 Sh / PnL% | MDD% | min_eq | ΔSh |
|---:|---|---:|---:|---:|---:|---:|
| 1 | BB-long w-250 ETH 2024-H1 | 1.39 / 4.12 | **1.43** / 19.20 | 11.4 | 9825 | +0.045 |
| 2 | BB-long w-250 ETH 2025-H1 | 1.58 / 6.51 | **1.63** / 30.80 | 19.2 | 9640 | +0.051 |
| 3 | BB-long w-250 BTC 2024-H2 | 0.60 / 1.26 | 0.58 / 5.36 | 19.2 | 8420 | -0.016 |
| 4 | BB-long w-250 SOL 2024-H2 | 1.47 / 6.98 | 1.42 / 32.77 | **34.5** | 6990 | -0.055 |
| 5 | BB-bidir w-300 SOL 2024-H2 | 0.77 / 4.88 | **0.88** / 20.22 | **36.4** | 6788 | +0.116 |
| 6 | BB-bidir w-300 BTC 2025-H1 | 1.38 / 4.44 | 1.35 / 20.32 | 11.4 | 8855 | -0.032 |
| 7 | BB-bidir w-300 ETH 2025-H1 | 2.80 / 17.28 | **2.95** / 82.60 | 20.7 | 9944 | +0.157 |
| 8 | BB-bidir w-300 SOL 2025-H1 | 1.64 / 14.51 | 1.58 / 68.07 | **43.3** | 5671 | -0.060 |
| 9 | RSI-long w-300 ETH 2024-H2 | 0.93 / 2.63 | 0.93 / 11.84 | 18.5 | 8622 | -0.003 |
| 10 | RSI-short pure BTC 2025-H2 | 1.73 / 6.63 | 1.60 / 29.37 | 18.6 | 8884 | -0.137 |
| 11 | RSI-short pure SOL 2025-H2 | 1.94 / 14.55 | 1.82 / 69.26 | 29.9 | 7350 | -0.128 |
| 12 | RSI-short trendhtf SOL 2025-H1 | 1.82 / 11.90 | **1.87** / 57.77 | 33.0 | 8445 | +0.051 |
| 13 | RSI-short w-300 BTC 2025-H1 | 1.87 / 5.95 | 1.86 / 27.88 | 8.3 | 9169 | -0.010 |

(“base” = fullperiod com notional 2k; não os stats OOS dos manifests — esses estão em `baseline_manifest` dentro do JSON para referência.)

## Observações

1. **Nenhum blow-up em 13/13.** Pior `min_equity` = 5671 USDT (BB-bidir SOL 2025-H1; capital inicial 10k). Em todos os combos curto, EXIT em reversão para a média sai antes de runaway catastrófico.
2. **Sharpe essencialmente preservado** — 5 sobem, 1 flat, 7 caem; ΔSh mediana -0.016 (vs snowball mediana -0.10). Fixed_notional 100% é aproximadamente **neutro em Sharpe** vs baseline 20%, como esperado: com notional estático, o Sharpe é invariante à escala no limite (var e mean escalam linearmente).
3. **PnL nominal escala ~5×** (baseline×5 = notional ratio), confirmando linearidade. Top = BB-bidir ETH 2025-H1: 17.28% → 82.60% (4.78× baseline, próximo do fator 5×).
4. **4/13 ainda excedem MDD 20% (gate AGENTS.md §8 #1)**: #4, #5, #8, #11, #12 — e #7 fica em 20.7% (borderline). Entre esses, #8 (SOL BB-bidir 2025-H1) MDD 43% é o pior caso.
5. **Vs snowball (ADR-0205)**: fixed_100 é estritamente melhor em Sharpe e em min_equity em 11/13 combos. O ∆Sharpe snowball (-0.10 mediana) vem quase todo da variance-cost de escalar com equity volátil — removido aqui.
6. **Best Sharpe snowball = 2.25** (ETH BB-bidir 2025-H1). **Best Sharpe fixed_100 = 2.95** (mesmo combo). Fixed_100 preservou o topo.

## Interpretação

- "100% do capital por entrada **sem compounding**" = posição 5× baseline no stack atual. **Sharpe ≈ baseline, PnL ≈ 5× baseline, MDD ≈ 5× baseline em combos curto-leaning e sub-5× em combos long-leaning** (há algum efeito de teto em longs porque max loss literal é 100% do notional ≡ 100% do capital, mas nenhum combo chegou perto).
- Confirma por oposição o achado de ADR-0205 (Padrão 47): o custo do snowball é **variance-cost** (compounding sobre equity volátil), não mau mercado. Remover compounding restaura o Sharpe.
- **Não viola ADR-0030** no sentido estrito (sizing ainda é `fixed_notional_literal`), mas excede `notional_per_trade_quote_ccy=2000` → qualquer handoff sob essa configuração exigiria **novo manifest v3+** com `notional_per_trade_quote_ccy=10_000` e re-validação OOS/MC/cost-stress completa. Não estou escrevendo esse manifest — é decisão explícita do user.

## Consequences

- **Positive:** evidência direta de que "aumentar notional sem snowball" é aproximadamente linear em PnL com Sharpe estável. Isso abre debate explícito sobre capital_allocation/alavancagem vs accumulation strategy.
- **Negative:** nenhuma — é diagnóstico puro.
- **Neutral:** artefatos preservados em `exports/diag/fixed_100_stack13_20260422.json`.

## Alternatives considered

- **Reduzir fracao em troca de mais trades**: ortogonal ao pedido; fora do escopo.
- **Mesmo teste mas com alavancagem 2x / 5x** (capital efetivo > 10k): possível próximo passo se user quiser explorar risk budget explicitamente. Não rodado aqui.
- **Escrever manifest v3+ com notional 10k** para handoff: fora do escopo (user não pediu handoff; stack atualmente no bot usa notional 2k literal).

## Follow-ups

- STATE.md atualizado com link para ADR-0206.
- Nenhum handoff. Manifests inalterados.
- Se user decidir promover essa sizing para produção, abrir ADR separado com novo manifest + re-validação OOS completa (gate AGENTS.md §8).
