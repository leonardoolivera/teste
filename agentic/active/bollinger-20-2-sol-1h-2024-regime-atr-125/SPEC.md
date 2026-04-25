# SPEC.md - Z.2 bollinger SOL 1h 2024 + atr_regime

> Gate: **pesquisa**. Série Z.

## Hipótese

SOL curve fill-in: between R.1(100) and R.2(150).

## Mercado

SOLUSDT spot, Binance Vision, 2024-07-05 -> 2024-12-31, 4320 barras 1h.

## Entradas

BollingerMeanReversionStrategy(20, 2.0, long_only=True) + `atr_regime:window=14:min_atr_bps=125`.

## Saídas

Edge-triggered. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

atr_regime (Série Z).
