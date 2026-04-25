# SPEC.md — Bollinger 20/2 BTC 15m 2024 (L.2)

> Gate: **pesquisa**. Segundo da Série L — cross-asset replication do achado de L.1.
> L.1 SOL 15m falhou critério 3 (spread+10/baseline=0.871). L.2 testa se quebra é
> intrínseca ao timeframe ou específica de SOL.

## Hipótese (§1)

**Se L.2 BTC 15m também falhar critério 3, fragilidade econômica em 15m é propriedade
do timeframe (alta frequência → custos cumulativos).** Se passar, L.1 foi idiossincrasia
de SOL.

## Mercado (§2)

BTCUSDT spot, Binance Vision. 2024-07-05 → 2024-12-31, **17280 barras 15m**.

## Entradas (§4)

ADR-0026 edge-triggered duplo, `window=20, num_std=2.0, long_only=True`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média. Custos H.1.

## Critério de refutação

ADR-0025 híbrido. Critério 3 é o gate decisivo (L.1 já evidencia risco).
