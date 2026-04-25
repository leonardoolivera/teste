# SPEC.md - W.1 bollinger SOL 1h 2025 + atr_regime

> Gate: **pesquisa**. Série W.

## Hipótese

OOS 2025-H2 test of R.1 sweet spot.

## Mercado

SOLUSDT spot, Binance Vision, 2025-07-05 -> 2025-12-31, 4320 barras 1h.

## Entradas

BollingerMeanReversionStrategy(20, 2.0, long_only=True) + `atr_regime:window=14:min_atr_bps=100`.

## Saídas

Edge-triggered. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

atr_regime (Série W).
