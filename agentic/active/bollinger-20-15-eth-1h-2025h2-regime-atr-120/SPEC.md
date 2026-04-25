# SPEC.md - AJ.6 bollinger ETH 1h 2025-H2 cross-window

> Gate: **pesquisa**. Serie AJ.

## Hipotese

ETH 20/1.5+atr:120 cross-window - testa se winner de AI (atr:120 em 2024-H2) mantem em 2025-H2.

## Mercado

ETHUSDT spot, Binance Vision, 20250705_20251231, ~4320 barras 1h.

## Entradas

BollingerMeanReversionStrategy (causal) + `atr_regime:window=14:min_atr_bps=120`.

## Saidas

Edge-triggered. Custos H.1.

## Criterio

ADR-0025 hibrido.

## Familia de filtro

atr_regime (Serie AJ - cross-window de vencedores AI.3/AI.4).
