# SPEC.md - AC.3 bollinger ETH 1h 2025

> Gate: **pesquisa**. Série AC.

## Hipótese

ETH thr=130 OOS 2025 - T.6 degrades.

## Mercado

ETHUSDT spot, Binance Vision, 2025-07-05 -> 2025-12-31, 4320 barras 1h.

## Entradas

BollingerMeanReversionStrategy (causal) + `atr_regime:window=14:min_atr_bps=130`.

## Saídas

Edge-triggered. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

atr_regime (Série AC).
