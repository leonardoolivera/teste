# SPEC.md - AK.7 bollinger ETH 1h 2025-H1 + bollinger_width

> Gate: **pesquisa**. Serie AK.

## Hipotese

ETH 20/1.5 + bollinger_width:250 em 2025-H1 - nova familia de filtro (volatilidade estrutural via largura de banda) ortogonal ao ATR (candle range).

## Mercado

ETHUSDT spot, Binance Vision, 20250105_20250704, ~4320 barras 1h.

## Entradas

BollingerMeanReversionStrategy (causal) + `bollinger_width:window=20:num_std=1.5:min_width_bps=250`.

## Saidas

Edge-triggered. Custos H.1.

## Criterio

ADR-0025 hibrido.

## Familia de filtro

bollinger_width (Serie AK - nova familia ortogonal ao atr_regime; extensao aditiva ADR-0022).
