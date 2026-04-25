# SPEC.md - AI.1 bollinger ETH 1h 2024-H2 sensibilidade

> Gate: **pesquisa**. Serie AI.

## Hipotese

20/1.25+atr:105 em ETH 2024-H2 - banda mais apertada aumenta trades sem perder edge.

## Mercado

ETHUSDT spot, Binance Vision, 2024-07-05 -> 2024-12-31, 4368 barras 1h.

## Entradas

BollingerMeanReversionStrategy (causal) + `atr_regime:window=14:min_atr_bps=105`.
num_std=1.25 (banda mais apertada que baseline 1.5).

## Saidas

Edge-triggered. Custos H.1.

## Criterio

ADR-0025 hibrido.

## Familia de filtro

atr_regime (Serie AI - sensibilidade parametrica em torno de U.2 baseline).
