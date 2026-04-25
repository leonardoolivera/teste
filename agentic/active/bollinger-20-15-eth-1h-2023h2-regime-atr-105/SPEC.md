# SPEC.md - AH.1 bollinger ETH 2023-H2 (Série AH)

> Gate: **pesquisa**. Série AH — cross-year (2023) e cross-timeframe (4h) para testar limites da config ETH 20/1.5+atr:105.

## Hipótese

Se ETH 20/1.5+atr:105 funciona em 2023-H2 (5ª janela) e em 4h 2024, edge é **estrutural** não calibrado.
Se falha em qualquer, edge tem limites (window-specific, timeframe-specific ou asset-specific).

## Mercado

ETHUSDT spot, Binance Vision, período 2023-H2.

## Entradas

BollingerMeanReversionStrategy(window=20, num_std=1.5) + `atr_regime:window=14:min_atr_bps=105`.

## Saídas

Edge-triggered long-only. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

atr_regime.
