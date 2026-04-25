# SPEC.md - V.1 bollinger BTC 1h 2024 + atr_regime

> Gate: **pesquisa**. Série V.

## Hipótese

BTC refine between P.2(50) and T.2(70).

## Mercado

BTCUSDT spot, Binance Vision, 2024-07-05 -> 2024-12-31, 4320 barras 1h.

## Entradas

BollingerMeanReversionStrategy(20, 2.0, long_only=True) + `atr_regime:window=14:min_atr_bps=55`.

## Saídas

Edge-triggered. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

atr_regime (Série V).
