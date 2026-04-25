# SPEC.md - AB.2 rsi ETH 1h 2024

> Gate: **pesquisa**. Série AB.

## Hipótese

RSI ETH + atr thr=90 - BEST RSI of protocol.

## Mercado

ETHUSDT spot, Binance Vision, 2024-07-05 -> 2024-12-31, 4320 barras 1h.

## Entradas

RSIMeanReversionStrategy(14, 30, 70) + `atr_regime:window=14:min_atr_bps=90`.

## Saídas

Edge-triggered. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

atr_regime (Série AB).
