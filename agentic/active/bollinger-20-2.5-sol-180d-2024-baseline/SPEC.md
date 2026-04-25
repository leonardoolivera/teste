# SPEC.md — Bollinger 20/2.5 SOL 180d 2024 (K.2)

> Gate: **pesquisa**. Segundo da Série K — banda mais larga (2.5σ).

## Hipótese (§1)

Edge sobrevive banda mais seletiva. Menos sinais, maior precisão esperada.

## Mercado (§2)

SOLUSDT spot 2024-07-05 → 2024-12-31, 4320 barras 1h.

## Entradas (§4)

ADR-0026 edge-triggered duplo, `window=20, num_std=2.5, long_only=True`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média. Custos H.1.

## Critério de refutação

ADR-0025 híbrido.
