# SPEC.md - AB.1 rsi SOL 1h 2024

> Gate: **pesquisa**. Série AB.

## Hipótese

RSI SOL + atr thr=100 (cross-family cross-asset).

## Mercado

SOLUSDT spot, Binance Vision, 2024-07-05 -> 2024-12-31, 4320 barras 1h.

## Entradas

RSIMeanReversionStrategy(14, 30, 70) + `atr_regime:window=14:min_atr_bps=100`.

## Saídas

Edge-triggered. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

atr_regime (Série AB).
