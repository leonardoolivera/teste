# SPEC.md - AF.2 bollinger ETH 1h 2025-H1 (Série AF)

> Gate: **pesquisa**. Série AF — primeira janela 2025-H1 para isolar window decay.

## Hipótese

Se edge preserva em 2025-H1 mas degrada em 2025-H2, degradação é **contínua no tempo** (mercado mudou durante 2025) — não "qualquer 2025 falha".

## Mercado

ETHUSDT spot, Binance Vision, 2025-01-05 -> 2025-07-04, 4344 barras 1h.

## Entradas

BollingerMeanReversionStrategy(window=20, num_std=1.5) + `atr_regime:window=14:min_atr_bps=105`.

## Saídas

Edge-triggered long-only. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

atr_regime (mesma config que AD/AC, OOS janela diferente).
