# SPEC.md — Bollinger 20/2 ETH 4h 2024 (M.3)

> Gate: **pesquisa**. Terceiro e último da Série M — fecha trio cross-asset 4h.

## Hipótese (§1)

**ETH 4h replicará padrão M.1/M.2** (critério 3 OK, fe < capital por amostra pequena).
Fecha a simetria formal vs Série L.

## Mercado (§2)

ETHUSDT spot, Binance Vision. 2024-07-05 → 2024-12-31, **1080 barras 4h**.

## Entradas (§4)

ADR-0026 edge-triggered duplo, `window=20, num_std=2.0, long_only=True`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média. Custos H.1.

## Critério de refutação

ADR-0025 híbrido + hipótese SPEC (fe > capital).
