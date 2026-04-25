# SPEC.md — Bollinger 20/2 BTC 4h 2024 (M.2)

> Gate: **pesquisa**. Segundo da Série M — replicação cross-asset do achado M.1.
> M.1 SOL 4h passou critérios 1-3 mas falhou hipótese SPEC (fe < capital).
> M.2 testa se fenômeno é cross-asset.

## Hipótese (§1)

**BTC 4h preservará critério 3 (poucos trades → poucos custos) mas provavelmente
não gerará edge por amostra pequena.** Se confirmado, 1h é sweet spot universal
para Bollinger 20/2 neste protocolo.

## Mercado (§2)

BTCUSDT spot, Binance Vision. 2024-07-05 → 2024-12-31, **1080 barras 4h**.

## Entradas (§4)

ADR-0026 edge-triggered duplo, `window=20, num_std=2.0, long_only=True`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média. Custos H.1.

## Critério de refutação

ADR-0025 híbrido + hipótese SPEC (fe > capital).
