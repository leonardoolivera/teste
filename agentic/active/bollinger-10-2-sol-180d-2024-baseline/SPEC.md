# SPEC.md — Bollinger 10/2 SOL 180d 2024 (K.3)

> Gate: **pesquisa**. Terceiro da Série K — janela curta (window=10).

## Hipótese (§1)

Edge sobrevive janela curta. Reatividade maior, mais sinais, risco de ruído.

## Mercado (§2)

SOLUSDT spot 2024-07-05 → 2024-12-31.

## Entradas (§4)

ADR-0026 edge-triggered duplo, `window=10, num_std=2.0, long_only=True`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média. Custos H.1.

## Critério de refutação

ADR-0025 híbrido.
