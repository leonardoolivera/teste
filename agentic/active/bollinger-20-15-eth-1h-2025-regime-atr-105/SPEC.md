# SPEC.md - AC.1 bollinger ETH 1h 2025

> Gate: **pesquisa**. Série AC.

## Hipótese

ETH 20/1.5 OOS 2025 - PRESERVES edge.

## Mercado

ETHUSDT spot, Binance Vision, 2025-07-05 -> 2025-12-31, 4320 barras 1h.

## Entradas

BollingerMeanReversionStrategy (causal) + `atr_regime:window=14:min_atr_bps=105`.

## Saídas

Edge-triggered. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

atr_regime (Série AC).
