# SPEC.md — Bollinger 20/2 SOLUSDT 1h 180d 2024 (J.1)

> Gate: **pesquisa**. Primeiro piloto Série J — teste de robustez temporal do edge
> mean-reversion validado na Série I (2025-H2). Mesma configuração de I.1, única
> diferença é a janela temporal (2024-07-05 → 2024-12-31 vs 2025-07-05 → 2025-12-31).

## Hipótese (§1)

**O edge mean-reversion (Bollinger 20/2 long-only) é estrutural da família sobre crypto 1h,
não específico da janela bull/lateral de 2025-H2.** Se J.1 cruza 45%, robustez temporal
corroborada (edge sobrevive regime não-correlato). Se refuta, edge de I.1 é artefato de
janela específica e estratégia não pode ir para handoff.

## Mercado (§2)

SOLUSDT spot, Binance Vision. Janela 2024-07-05 → 2024-12-31, 4320 barras 1h.
**Dataset não-correlato com Série I** (separação temporal completa, 6 meses de gap).

## 3. Timeframe

1h OHLCV. Idêntico a I.1/I.2/I.3 — única diferença é janela.

## Entradas (§4)

Idêntico a I.1 — ADR-0026, edge-triggered duplo em banda inferior, `window=20, num_std=2.0, long_only=True`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média (ADR-0026).

## 6-11-bis

Custos H.1 (5/2/0 bps); `fracao=0.1, alav=2.0`; sem stops; sem filtro.

## Critério de refutação (sob ADR-0025)

1. `hit_rate baseline ≥ 45%`.
2. `max_drawdown ≤ 35%`.
3. `spread+10 / baseline ≥ 0.95`.
4. Rank top-3 para `paper_only`.

**Experimento controlado:** `compare` I.1 ↔ J.1 → 2 flags diff (`dataset_id`, `run_id`).
