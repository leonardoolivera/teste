# SPEC.md - AE.4 bollinger SOL 1h 2024 (Série AE)

> Gate: **pesquisa**. Série AE — in-sample 2024 de 20/1.5 cross-asset.

## Hipótese

**num_std=1.5 tem edge in-sample em BTC/SOL 2024-H2** (separa window-specificity de asset-specificity).
Se 1.5 std funciona em 2024 mas falha em 2025 → problema é cross-window.
Se 1.5 std falha em ambos → problema é asset (ETH-only).

## Mercado

SOLUSDT spot, Binance Vision, 2024-07-05 -> 2024-12-31, 4320 barras 1h.

## Entradas

BollingerMeanReversionStrategy(window=20, num_std=1.5) + (sem filtro — controle).

## Saídas

Edge-triggered long-only. Custos H.1.

## Critério

ADR-0025 híbrido.

## Família de filtro

baseline (nenhum — controle AE)
