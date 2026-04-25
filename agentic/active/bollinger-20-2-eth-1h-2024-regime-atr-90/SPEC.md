# SPEC.md - T.5 Bollinger 20/2 ETH 1h 2024 + atr_regime:90

> Gate: **pesquisa**. Série T - threshold sweep cross-asset.

## Hipótese

Threshold `atr_regime:14:90` em ETH 1h 2024-H2 mapeia ponto da curva. near ETH median (88.7) - SWEET SPOT candidate: fe 10645, hit 75%, ratio 0.9819. Método 3-pontos deve replicar forma vista em SOL (Série R).

## Mercado

ETHUSDT spot, Binance Vision, 2024-07-05 → 2024-12-31, 4320 barras 1h.

## Entradas

Bollinger `window=20, num_std=2.0, long_only=True` + `atr_regime:window=14:min_atr_bps=90`.

## Saídas

Edge-triggered mean exit. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

`atr_regime` (Série T: 3 pontos por asset).
