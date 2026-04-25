# SPEC.md - AJ.2 bollinger ETH 1h 2025-H1 cross-window

> Gate: **pesquisa**. Serie AJ.

## Hipotese

ETH 20/1.5+atr:90 cross-window - testa se winner de AI (atr:90 em 2024-H2) mantem em 2025-H1.

## Mercado

ETHUSDT spot, Binance Vision, 20250105_20250704, ~4320 barras 1h.

## Entradas

BollingerMeanReversionStrategy (causal) + `atr_regime:window=14:min_atr_bps=90`.

## Saidas

Edge-triggered. Custos H.1.

## Criterio

ADR-0025 hibrido.

## Familia de filtro

atr_regime (Serie AJ - cross-window de vencedores AI.3/AI.4).
