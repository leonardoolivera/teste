# SERIES_BO.md — Bollinger regime_filter min_width_bps sensitivity sweep

> Gate: **pesquisa**. Série BO. Aberta 2026-04-19. **Fechada 2026-04-19 com verdict Pareto estreito (2/8 PASS) → ADR-0035.**

## Verdict final (2026-04-19)

**2/8 PASS** — Pareto estreito (pior classe de todas as séries). Emitido [ADR-0035](../../decisions/0035-bollinger-min-width-bps-sensitivity-sweep-bo.md).

| Combo | bw=200 | bw=300 | Classe min_width_bps |
|---|---|---|---|
| ETH 2024-H1 | ❌ | ❌ | fragile_both |
| ETH 2025-H1 | ❌ (MC p5) | ✅ (Sharpe 2.07) | fragile_low |
| BTC 2024-H2 | ❌ | ❌ (trades=21) | fragile_both |
| SOL 2024-H2 | ✅ (Sharpe 2.05) | ❌ (MC p5) | fragile_high |

**Pareto 3D consolidado (BK × BN × BO):**

| Combo | Classe 3D |
|---|---|
| ETH 2024-H1 | fragile_3d_totalmente_frágil |
| ETH 2025-H1 | semi_robust_num_std |
| BTC 2024-H2 | fragile_3d |
| SOL 2024-H2 | semi_robust_window |

**Nenhum combo é robust em todos 3 eixos.** Config v2 é um ótimo local fino.


## Hipótese

Séries BK (num_std) e BN (window) mapearam 2 eixos do Pareto dos 4 combos v2.
BO completa o Pareto testando o 3º eixo: `min_width_bps` do regime filter
`bollinger_width`.

Baseline v2: `min_width_bps=250`. Perturbação ±20%:
- BO.lo: `min_width_bps=200` (gate mais permissivo → mais sinais admitidos)
- BO.hi: `min_width_bps=300` (gate mais restritivo → menos sinais)

Engine params (window=30, num_std=1.5) e regime filter internals (window=20,
num_std=2) permanecem fixos.

## Matriz (8 pilotos)

| Combo | BO.lo (250→200) | BO.hi (250→300) |
|---|---|---|
| ETH 1h 2024-H1 | BO.1 | BO.5 |
| ETH 1h 2025-H1 | BO.2 | BO.6 |
| BTC 1h 2024-H2 | BO.3 | BO.7 |
| SOL 1h 2024-H2 | BO.4 | BO.8 |

## Gates strict (mesmos BK/BN)

`trades ≥ 30`, `Sharpe ≥ 1.0`, `MDD ≤ 20%`, `PnL > 0`, `cost_stress_ratio_min ≥ 0.95`,
`MC p5 final_equity > 10000`, `MC MDD p95 ≤ 10%`.

## Critério de decisão

- **≥ 6/8 PASS:** Pareto 3D robusto, nota informativa ADR-0033.
- **3-5/8 PASS:** Pareto médio no 3º eixo. ADR-BO marca fragilidade.
- **≤ 2/8 PASS:** Pareto estreito. Regime gate é ponto singular — forte risco de
  overfitting do `min_width_bps=250` escolhido em ADR-0028.

## Fora de escopo

- Perturbação simultânea de 2 eixos (interaction effects) — Série BP se BO sobreviver.
- Perturbação do `window` e `num_std` internos do regime filter (não dos Bollinger
  da estratégia) — adiado.
