# SPEC.md - AA.1 bollinger ETH 1h 2024

> Gate: **pesquisa**. Série AA.

## Hipótese

Bollinger window=10 at U.2 sweet spot.

## Mercado

ETHUSDT spot, Binance Vision, 2024-07-05 -> 2024-12-31, 4320 barras 1h.

## Entradas

BollingerMeanReversionStrategy (causal) + `atr_regime:window=14:min_atr_bps=105`.

## Saídas

Edge-triggered. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

atr_regime (Série AA).
