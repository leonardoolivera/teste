# SPEC.md - T.2 Bollinger 20/2 BTC 1h 2024 + atr_regime:70

> Gate: **pesquisa**. Série T - threshold sweep cross-asset.

## Hipótese

Threshold `atr_regime:14:70` em BTC 1h 2024-H2 mapeia ponto da curva. near BTC median ATR (70.7) - mid-curve; lower trades but fe preserved. Método 3-pontos deve replicar forma vista em SOL (Série R).

## Mercado

BTCUSDT spot, Binance Vision, 2024-07-05 → 2024-12-31, 4320 barras 1h.

## Entradas

Bollinger `window=20, num_std=2.0, long_only=True` + `atr_regime:window=14:min_atr_bps=70`.

## Saídas

Edge-triggered mean exit. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

`atr_regime` (Série T: 3 pontos por asset).
