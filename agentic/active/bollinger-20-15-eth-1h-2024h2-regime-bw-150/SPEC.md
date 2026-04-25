# SPEC.md - AK.2 bollinger ETH 1h 2024-H2 + bollinger_width

> Gate: **pesquisa**. Serie AK.

## Hipotese

ETH 20/1.5 + bollinger_width:150 em 2024-H2 - nova familia de filtro (volatilidade estrutural via largura de banda) ortogonal ao ATR (candle range).

## Mercado

ETHUSDT spot, Binance Vision, 20240705_20241231, ~4320 barras 1h.

## Entradas

BollingerMeanReversionStrategy (causal) + `bollinger_width:window=20:num_std=1.5:min_width_bps=150`.

## Saidas

Edge-triggered. Custos H.1.

## Criterio

ADR-0025 hibrido.

## Familia de filtro

bollinger_width (Serie AK - nova familia ortogonal ao atr_regime; extensao aditiva ADR-0022).
