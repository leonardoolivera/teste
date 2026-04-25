# SPEC.md — Bollinger 50/2 SOL 180d 2024 (K.4)

> Gate: **pesquisa**. Quarto da Série K — janela longa (window=50).

## Hipótese (§1)

Edge sobrevive janela longa. Menor reatividade, menos sinais, robustez a ruído.

## Mercado (§2)

SOLUSDT spot 2024-07-05 → 2024-12-31.

## Entradas (§4)

ADR-0026 edge-triggered duplo, `window=50, num_std=2.0, long_only=True`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média. Custos H.1.

## Critério de refutação

ADR-0025 híbrido.
