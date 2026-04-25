# SPEC.md — Bollinger 20/2 SOL 15m 2024 (L.1)

> Gate: **pesquisa**. Primeiro da Série L — teste de robustez cross-timeframe.
> Todos os 22 pilotos anteriores rodam em 1h; L testa se edge sobrevive em 15m.

## Hipótese (§1)

**Edge mean-reversion sobrevive timeframe menor (15m).** Se passa ADR-0025, edge é
propriedade da família; se quebra, edge é específico de 1h.

## Mercado (§2)

SOLUSDT spot, Binance Vision. 2024-07-05 → 2024-12-31, **17280 barras 15m** (4× mais
que 1h).

## Entradas (§4)

ADR-0026 edge-triggered duplo, `window=20, num_std=2.0, long_only=True`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média. Custos H.1.

## Critério de refutação

ADR-0025 híbrido. **Atenção especial ao critério 3** (spread+10/baseline ≥ 0.95):
timeframe menor = mais trades = maior exposição a custos.
