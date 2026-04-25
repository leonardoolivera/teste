# SPEC.md — Bollinger 20/2 ETHUSDT 1h 180d 2024 (J.3)

> Gate: **pesquisa**. Terceiro piloto Série J — cross-window ETH. Fecha trio J.1+J.2+J.3.

## Hipótese (§1)

**Edge mean-reversion ETH 1h sobrevive janela temporal não-correlata.** I.3 hit=63.41%
em 2025-H2; J.3 testa 2024-H2.

## Mercado (§2)

ETHUSDT spot, Binance Vision. 2024-07-05 → 2024-12-31, 4320 barras.

## Entradas (§4)

ADR-0026 edge-triggered duplo, `window=20, num_std=2.0, long_only=True`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média. Custos H.1.

## Critério de refutação

ADR-0025 híbrido.
