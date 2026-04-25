# SPEC.md - AD.1 bollinger BTC 1h 2025 (Série AD)

> Gate: **pesquisa**. Série AD — generalização cross-asset de AC.1.

## Hipótese

**num_std=1.5 preserva edge OOS 2025 cross-asset** (replicando AC.1 ETH em BTC/SOL).
AD.3 (ETH sem filtro) isola se ganho vem de 1.5 std ou da combinação 1.5+filtro.

## Mercado

BTCUSDT spot, Binance Vision, 2025-07-05 -> 2025-12-31, 4320 barras 1h.

## Entradas

BollingerMeanReversionStrategy (causal) + regime `atr_regime:window=14:min_atr_bps=55`.

## Saídas

Edge-triggered. Custos H.1 (fee 5 bps, slip 1, spread 0).

## Critério

ADR-0025 híbrido.

## Família de filtro

atr_regime (Série AD)
