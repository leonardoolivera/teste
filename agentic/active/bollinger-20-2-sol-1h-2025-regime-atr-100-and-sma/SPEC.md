# SPEC.md - AC.2 bollinger SOL 1h 2025

> Gate: **pesquisa**. Série AC.

## Hipótese

SOL AND OOS 2025 - AND does not help cross-window.

## Mercado

SOLUSDT spot, Binance Vision, 2025-07-05 -> 2025-12-31, 4320 barras 1h.

## Entradas

BollingerMeanReversionStrategy (causal) + `and(atr_regime:window=14:min_atr_bps=100,sma_slope:window=50:min_slope_bps=10)`.

## Saídas

Edge-triggered. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

Composite AND (Série AC).
