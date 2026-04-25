# SPEC.md — Bollinger 20/2 ETH 15m 2024 (L.3)

> Gate: **pesquisa**. Terceiro e último da Série L — fecha trio cross-asset em 15m.
> L.1 SOL e L.2 BTC ambos falharam critério 3. L.3 ETH confirma ou refuta a
> propriedade do timeframe.

## Hipótese (§1)

**ETH 15m replicará o mesmo padrão de fragilidade (spread+10/baseline < 0.95).**
Se sim, achado é formal (3/3 assets). Se não, padrão é bi-asset mas não universal.

## Mercado (§2)

ETHUSDT spot, Binance Vision. 2024-07-05 → 2024-12-31, **17280 barras 15m**.

## Entradas (§4)

ADR-0026 edge-triggered duplo, `window=20, num_std=2.0, long_only=True`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média. Custos H.1.

## Critério de refutação

ADR-0025 híbrido. Critério 3 é o gate decisivo.
