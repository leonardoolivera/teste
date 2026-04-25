# SPEC.md - T.1 Bollinger 20/2 BTC 1h 2024 + atr_regime:35

> Gate: **pesquisa**. Série T - threshold sweep cross-asset.

## Hipótese

Threshold `atr_regime:14:35` em BTC 1h 2024-H2 mapeia ponto da curva. below q15 BTC ATR (46.5) - filter mostly inactive, few extra signals. Método 3-pontos deve replicar forma vista em SOL (Série R).

## Mercado

BTCUSDT spot, Binance Vision, 2024-07-05 → 2024-12-31, 4320 barras 1h.

## Entradas

Bollinger `window=20, num_std=2.0, long_only=True` + `atr_regime:window=14:min_atr_bps=35`.

## Saídas

Edge-triggered mean exit. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

`atr_regime` (Série T: 3 pontos por asset).
