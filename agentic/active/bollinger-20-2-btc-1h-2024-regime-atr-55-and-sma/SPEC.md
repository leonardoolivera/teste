# SPEC.md - X.1 bollinger BTC 1h 2024 + composite

> Gate: **pesquisa**. Série X.

## Hipótese

BTC AND filter at V.1 sweet spot.

## Mercado

BTCUSDT spot, Binance Vision, 2024-07-05 -> 2024-12-31, 4320 barras 1h.

## Entradas

BollingerMeanReversionStrategy(20, 2.0, long_only=True) + `and(atr_regime:window=14:min_atr_bps=55,sma_slope:window=50:min_slope_bps=10)`.

## Saídas

Edge-triggered. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

Composite AND (Série X).
