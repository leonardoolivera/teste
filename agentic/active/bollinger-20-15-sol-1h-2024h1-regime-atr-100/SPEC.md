# SPEC.md - AG.3 bollinger SOL 1h 2024-H1 (Série AG)

> Gate: **pesquisa**. Série AG — 4ª janela OOS para corroborar/refutar estabilidade cross-window.

## Hipótese

Se ETH preserva edge em 4 janelas distintas (2024-H1, 2024-H2, 2025-H1, 2025-H2), estabilidade está consolidada — candidato forte para deploy.
Se ETH falha em 2024-H1, 2024-H2 pode ser outlier.

## Mercado

SOLUSDT spot, Binance Vision, 2024-01-05 -> 2024-07-04, 4368 barras 1h.

## Entradas

BollingerMeanReversionStrategy(window=20, num_std=1.5) + `atr_regime:window=14:min_atr_bps=100`.

## Saídas

Edge-triggered long-only. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

atr_regime.
