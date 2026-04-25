# SPEC.md - Y.1 donchian BTC 1h 2024 + atr_regime

> Gate: **pesquisa**. Série Y.

## Hipótese

Donchian BTC + atr - cross-strategy filter test.

## Mercado

BTCUSDT spot, Binance Vision, 2024-07-05 -> 2024-12-31, 4320 barras 1h.

## Entradas

DonchianBreakoutStrategy(20, 10, long_only=True) + `atr_regime:window=14:min_atr_bps=55`.

## Saídas

Edge-triggered. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

atr_regime (Série Y).
