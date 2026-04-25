# SERIES_BK.md — Bollinger num_std sensitivity sweep

> Gate: **pesquisa**. Série BK. Aberta 2026-04-18. **Fechada 2026-04-19 com verdict Pareto médio (4/8 PASS) → ADR-0032.**

## Verdict final (2026-04-19)

**4/8 PASS** — Pareto médio. Emitido [ADR-0032](../../decisions/0032-bollinger-num-std-sensitivity-sweep-bk.md).

| Combo | ns=1.25 | ns=1.75 | Classe |
|---|---|---|---|
| ETH 2024-H1 | BK.1 ✅ | BK.5 ❌ (Sharpe 0.70) | fragile_high |
| ETH 2025-H1 | BK.2 ✅ | BK.6 ✅ | **robust** |
| BTC 2024-H2 | BK.3 ❌ (MC p5) | BK.7 ❌ (MC p5) | fragile_both |
| SOL 2024-H2 | BK.4 ❌ (MC p5) | BK.8 ✅ | fragile_low |

Tabela completa: `exports/diag/bk_sweep_summary.json`.


## Hipótese

Os 4 combos aprovados pela ADR-0028 (ETH 2024-H1, SOL 2024-H1, SOL 2024-H2, BTC 2025-H1)
rodam com `window=30 × num_std=1.5`. BK testa se o Pareto aguenta perturbação de
`num_std` em ±16.7% mantendo o regime gate `bollinger_width:250` e a janela 30.

Se os 4 combos sobreviverem `num_std ∈ {1.25, 1.75}` com OOS Sharpe ≥ 1.0, MDD ≤ 20%,
PnL > 0 e trades ≥ 30, o ponto `ns=1.5` não é singular — reduz risco de overfitting
em parametrização fina. Se metade cair, o Pareto é estreito e a aprovação v2 precisa
de nota de robustez.

## Perturbação

- Baseline (aprovado v2): `window=30, num_std=1.5` (imutável)
- BK.lo: `window=30, num_std=1.25` (bandas mais estreitas → mais sinais, mais ruído)
- BK.hi: `window=30, num_std=1.75` (bandas mais largas → menos sinais, mais seletivo)

Mercado, regime gate (`bollinger_width:w=20:ns=2.0:min=250`), fees, slippage e
contratro runtime-faithful (ADR-0030) permanecem idênticos ao baseline.

## Matriz (8 pilotos) — combos do manifest v2 (ADR-0029)

| Combo | BK.lo (ns=1.25) | BK.hi (ns=1.75) |
|---|---|---|
| ETH 1h 2024-H1 | BK.1 ✅ | BK.5 |
| ETH 1h 2025-H1 | BK.2 | BK.6 |
| BTC 1h 2024-H2 | BK.3 | BK.7 |
| SOL 1h 2024-H2 | BK.4 | BK.8 |

**Correção 2026-04-19:** versão inicial do SPEC tinha SOL 2024-H1 e BTC 2025-H1 por engano — não são combos aprovados. Corrigido pra refletir `approved_combos` do manifest v2.

## Protocolo por piloto

1. Walk-forward 4-fold na mesma janela OOS do baseline v2.
2. Cost stress (fee +10%, slippage +20%) — ratio ≥ 0.95.
3. Monte Carlo bootstrap 1000, p5 PnL.
4. Lookahead guard em todas as features.
5. Comparação lado-a-lado com baseline v2: Δ Sharpe, Δ MDD, Δ PnL, Δ trades.

## Critério de decisão (séries completa)

- **Sobreviveram ≥ 7 de 8**: Pareto robusto. Registrar em nota informativa do ADR-0028.
- **Sobreviveram 4-6 de 8**: Pareto médio. Emitir ADR-BK com os sobreviventes e marcar combos frágeis.
- **Sobreviveram ≤ 3 de 8**: Pareto estreito. ADR-BK deprecia combos frágeis e investiga se ns=1.5 foi overfit.

## Ordem de execução

BK.1 primeiro (ETH 2024-H1 ns=1.25) como prova-de-conceito do pipeline.
Se BK.1 passa strict gates, abre BK.2–BK.8 em paralelo.
Se BK.1 falha gate fácil, reavalia a hipótese antes de seguir.

## Fora de escopo

- Cross-asset novo (DOT/AVAX/LINK) — adiado para Série BL.
- Cross-timeframe (4h, 15m) — adiado para Série BM.
- Perturbação de window (25, 35) — adiado para Série BN se BK aprovar.
