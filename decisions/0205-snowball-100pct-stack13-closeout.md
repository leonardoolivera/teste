# 0205 — Snowball 100%/entrada stack 13 (closeout diagnóstico)

**Status:** Accepted
**Date:** 2026-04-22
**Deciders:** Usuário + agente
**Relates to:** ADR-0204 (pré-reg), ADR-0030 (faithful sizing invariant), ADR-0029 (BotBinance reporta snowball degrada ETH), ADR-0063 (SizingMode.SNOWBALL).

## Resultado (13/13 combos)

Artefato: [`exports/diag/snowball_100_stack13_20260422.json`](../exports/diag/snowball_100_stack13_20260422.json). Script: [`scripts/run_snowball_100_stack13.py`](../scripts/run_snowball_100_stack13.py).

Sizing A (comparação apples-to-apples no período): `fracao=0.1, alav=2.0, fixed_notional` (match `notional_per_trade_quote_ccy=2000` dos manifests).
Sizing B (100%/entrada): `fracao=1.0, alav=1.0, snowball` — cada ENTER consome `capital_inicial + realized_pnl`.

Cost model baseline: 5 bps fee + 2 bps slip/notional + 0 bps spread (~14 bps round-trip, match manifests).

| # | Combo | base Sh | base PnL% | snow Sh | snow PnL% | MDD% | min_eq | ΔSh |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | BB-long w-250 ETH 2024-H1 | 1.39 | 4.12 | 1.26 | 18.70 | 13.3 | 9806 | -0.13 |
| 2 | BB-long w-250 ETH 2025-H1 | 1.58 | 6.51 | 1.43 | 30.38 | 22.8 | 9327 | -0.15 |
| 3 | BB-long w-250 BTC 2024-H2 | 0.60 | 1.26 | 0.51 | 4.51 | 19.3 | 8407 | -0.10 |
| 4 | BB-long w-250 SOL 2024-H2 | 1.47 | 6.98 | 1.42 | 33.75 | 32.3 | 7231 | -0.05 |
| 5 | BB-bidir w-300 SOL 2024-H2 | 0.77 | 4.88 | 0.72 | 13.63 | 36.4 | 6762 | -0.05 |
| 6 | BB-bidir w-300 BTC 2025-H1 | 1.38 | 4.44 | 1.31 | 20.86 | 11.1 | 8894 | -0.07 |
| 7 | BB-bidir w-300 ETH 2025-H1 | 2.80 | 17.28 | 2.25 | 90.66 | 40.1 | 9940 | -0.55 |
| 8 | BB-bidir w-300 SOL 2025-H1 | 1.64 | 14.51 | 1.56 | 67.16 | 39.7 | 6027 | -0.08 |
| 9 | RSI-long w-300 ETH 2024-H2 | 0.93 | 2.63 | 0.87 | 11.42 | 19.2 | 8553 | -0.06 |
| 10 | RSI-short pure BTC 2025-H2 | 1.73 | 6.63 | 1.54 | 30.07 | 19.6 | 8755 | -0.19 |
| 11 | RSI-short pure SOL 2025-H2 | 1.94 | 14.55 | 1.89 | 77.78 | 29.8 | 7350 | -0.05 |
| 12 | RSI-short trendhtf SOL 2025-H1 | 1.82 | 11.90 | 1.69 | 59.84 | 37.0 | 7998 | -0.13 |
| 13 | RSI-short w-300 BTC 2025-H1 | 1.87 | 5.95 | 1.75 | 29.43 | 8.4 | 9175 | -0.12 |

## Observações

1. **Nenhum blow-up** em 13/13. Pior `min_equity` = 6027 USDT (BB-bidir SOL 2025-H1; capital inicial 10k). Capital_corrente nunca foi ≤ 0 — zero rejeições por sizing.
2. **Sharpe degrada em 13/13** (ΔSh ∈ [-0.55, -0.05], mediana -0.10). Snowball 100% **não preserva edge risk-adjusted em nenhum combo**.
3. **PnL nominal multiplica 2.8× a 5.4×**: compounding agressivo amplifica retornos absolutos no período inteiro (esperado — capital cresce, cada trade movimenta mais notional).
4. **MDD escalar em 11-40%**; mediana 22.8%. **7/13 combos excedem o gate AGENTS.md §8 #1 (MDD ≤ 20%)** sob snowball 100% — invalidando-os para handoff se essa sizing fosse adotada.
5. **Assimetria long vs short**: combos long (#1-4, #9) MDD 13-32%; combos short/bidir (#5-8, #10-13) MDD 8-40%. Short não produziu blow-up apesar do risco teórico ilimitado, porque EXIT em reversão para a média sai antes do runaway.
6. **Top nominal** = BB-bidir ETH 2025-H1 (Sh 2.25, PnL +90.7%, MDD 40.1%). Top Sharpe snowball também = BB-bidir ETH 2025-H1. Mesmo top case: Sharpe cai 20% vs baseline.

## Interpretação

- **Confirma ADR-0030/Padrão de snowball**: compounding sobre equity volátil injeta variance-cost mesmo quando PnL médio é positivo. Padrão já conhecido (ADR-0029 BotBinance: ETH snowball +19% → +0.78%; Padrão 47 pyramid degrada 30-63%). Aqui os resultados offline são mais benignos que o caso BotBinance porque (a) rodei full-period vs OOS only, (b) custos baseline mais baixos que stress de BotBinance.
- **Teto prático de sharpe sob 100%/entrada**: para o stack atual, sharpe snowball nunca supera 2.25. Se a métrica-alvo é Sharpe, snowball é estritamente pior. Se a métrica-alvo é PnL nominal acumulado com aceite de MDD 20-40%, snowball entrega 2.8-5.4× mais.
- **Nenhum achado promove**. Manifests ficam inalterados, `disallow_sizing_modes: ["snowball",...]` mantido, `runtime_contract: faithful` / `sizing: fixed_notional_literal` permanecem invariantes do handoff.

## Consequences

- **Positive:** evidência numérica consolidada para o debate "por que não 100%?". Tabela diagnóstica que o user pode consultar diretamente quando a pergunta ressurgir.
- **Negative:** consome ~10 min de compute; não gera nova estratégia nem promove/rejeita combos existentes. Apenas informa.
- **Neutral:** artefato `exports/diag/snowball_100_stack13_20260422.json` preservado para re-uso (ex. comparar com runs futuros se stack for expandido).

## Alternatives considered

- **Walk-forward + MC por combo**: não adiciona informação relevante para a pergunta ("o que acontece com 100%?") — full-period revela a curva de compounding completa. Custo ~2h10 de compute. Rejeitado.
- **Leverage 2× ou maior com fixed notional**: fora do escopo imediato do pedido. Pode virar ADR separado se user quiser.
- **Kelly / Kelly-fracional**: também proibido por `disallow_sizing_modes`. Fora de escopo.

## Follow-ups

- Tabela de resultados em [`exports/diag/snowball_100_stack13_20260422.json`](../exports/diag/snowball_100_stack13_20260422.json).
- STATE.md atualizado com link para ADRs 0204/0205.
- Nenhum handoff ao BotBinance. Nenhum manifest novo. Nenhum ajuste na stack.
