# SPEC.md — Bollinger 20/2 BTCUSDT 1h 180d (I.2)

> Gate: **pesquisa**. Segundo piloto Série I — generalização cross-asset do edge
> mean-reversion observado em I.1 (SOL). Cross-asset replica com mesma janela e mesmos
> hiperparâmetros que I.1; única diferença é `dataset_id`.

## Hipótese (§1)

**O edge mean-reversion observado em SOL 1h 180d (I.1: hit=65.85%) é propriedade da
família Bollinger em crypto 1h, não propriedade específica de SOL.** Teste concreto: se
BTC 1h mesma janela cruza 45%, confirma família como primeira dimensão; se refuta, edge
é asset-específico ao SOL (componente oscilatório dominante naquele ativo/período).

## Mercado (§2)

BTCUSDT spot, Binance Vision. Mesma janela 2025-07-05 → 2025-12-31, 4320 barras 1h.

## 3. Timeframe

1h OHLCV. Idêntico a H.1 (Donchian BTC) e H.2b (MA BTC) — cross-family direto.

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

**Experimento controlado:** `compare` I.1 (SOL) ↔ I.2 (BTC) → 2 flags diff
(`dataset_id`, `run_id`).
