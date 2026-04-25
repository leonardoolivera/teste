# SERIES_BN.md — Bollinger window sensitivity sweep

> Gate: **pesquisa**. Série BN. Aberta 2026-04-19. **Fechada 2026-04-19 com verdict Pareto médio (4/8 PASS) → ADR-0033.**

## Verdict final (2026-04-19)

**4/8 PASS** — Pareto médio. Emitido [ADR-0033](../../decisions/0033-bollinger-window-sensitivity-sweep-bn.md).

| Combo | w=25 | w=35 | Classe window | Cross-axis 2D |
|---|---|---|---|---|
| ETH 2024-H1 | BN.1 ❌ (Sharpe 0.87) | BN.5 ❌ (MC p5) | fragile_both | **fragile_2d** |
| ETH 2025-H1 | BN.2 ❌ (MC p5) | BN.6 ✅ | fragile_low | semi_robust_num_std |
| BTC 2024-H2 | BN.3 ❌ (trades=29) | BN.7 ✅ | fragile_low | fragile_2d |
| SOL 2024-H2 | BN.4 ✅ | BN.8 ✅ | **robust** | semi_robust_window |

Tabela completa: `exports/diag/bn_sweep_summary.json`.

**Primeira onda paper (ADR-0033):** ETH 2025-H1 + SOL 2024-H2 (ambos `semi_robust`, diferentes eixos).
**Segunda onda (sizing reduzido):** BTC 2024-H2 + ETH 2024-H1 (ambos `fragile_2d`).


## Hipótese

Os 4 combos aprovados no manifest v2 (ADR-0029) rodam com `window=30 × num_std=1.5`.
Série BK (ADR-0032) mapeou o eixo `num_std` e marcou 3 dos 4 combos como frágeis em
±16.7% de perturbação. Falta o eixo `window`.

BN testa se `window ∈ {25, 35}` mantém gates strict nos 4 combos com `num_std=1.5`
fixo e regime gate bw_250 inalterado. Objetivo: fechar Pareto 2D (window × num_std)
antes de qualquer rollout paper.

Se ≥6/8 PASS: Pareto largo no eixo window, deploy pode relaxar para janela próxima.
Se 3-5/8 PASS: Pareto médio, confirma marcação de fragilidade do ADR-0032.
Se ≤2/8 PASS: o ponto window=30 é estreito; combinado com BK indica overfit 2D.

## Perturbação

- Baseline (aprovado v2): `window=30, num_std=1.5` (imutável)
- BN.lo: `window=25, num_std=1.5` (janela curta → mais ruído, mais sinais)
- BN.hi: `window=35, num_std=1.5` (janela longa → mais suave, menos sinais)

Regime gate (`bollinger_width:window=20:num_std=2.0:min_width_bps=250`), num_std,
fees, slippage, e contrato runtime-faithful (ADR-0030) permanecem idênticos ao
baseline v2.

## Matriz (8 pilotos)

| Combo | BN.lo (w=25) | BN.hi (w=35) |
|---|---|---|
| ETH 1h 2024-H1 | BN.1 | BN.5 |
| ETH 1h 2025-H1 | BN.2 | BN.6 |
| BTC 1h 2024-H2 | BN.3 | BN.7 |
| SOL 1h 2024-H2 | BN.4 | BN.8 |

## Protocolo por piloto

Mesmo pipeline da Série BK:

1. Walk-forward 4-fold na mesma janela OOS do baseline v2.
2. Cost stress (fee +10%, spread +10%) — ratio ≥ 0.95.
3. Monte Carlo bootstrap 1000 resamples, seed=42, p5 final_equity > 10000.
4. Lookahead guard (ADR-0002) em todas as features.
5. Comparação lado-a-lado com baseline v2 e com BK.1-BK.8 (eixo num_std).

## Critério de decisão (série completa)

- **≥ 6/8 PASS**: Pareto robusto no window. Registrar em nota informativa do ADR-0032.
- **3-5/8 PASS**: Pareto médio. Emitir ADR-BN marcando fragilidade 2D.
- **≤ 2/8 PASS**: Pareto estreito. ADR-BN deprecia combos frágeis em ambos eixos.

## Integração com ADR-0032

Classes `robustness.num_std_sensitivity` do manifest v2 serão cruzadas com
`robustness.window_sensitivity` (novo campo a adicionar):

- `robust` em ambos eixos → combo-líder confiável (candidato forte pra paper).
- `fragile_*` em só um eixo → deploy com sizing reduzido.
- `fragile_*` em ambos → não-ativar sem Série adicional (regime, timeframe).

## Ordem de execução

Os 8 pilotos rodam em batch via `tools/run_bn_sweep.py` (reuso do padrão de BK).
Sem piloto prova-de-conceito — BK.1 já validou que o pipeline está correto e que
perturbação pequena de parâmetro não quebra o engine.

## Fora de escopo

- Cross-timeframe (4h, 15m) — Série BL.
- Cross-asset (DOT/AVAX/LINK) — Série BM.
- Perturbação de `min_width_bps` do regime gate — adiado para Série BO.
- Perturbação combinada `window × num_std` fora dos 4 cantos — adiado; 8 pontos extras
  nos cantos `(25, 1.25)`, `(25, 1.75)`, `(35, 1.25)`, `(35, 1.75)` seriam Série BO
  se BN sobreviver.
