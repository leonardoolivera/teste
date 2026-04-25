# SPEC.md — Bollinger 20/2 BTCUSDT 1h 180d 2024 (J.2)

> Gate: **pesquisa**. Segundo piloto Série J — cross-window para BTC. J.1 validou edge
> temporal em SOL; J.2 testa se robustez temporal é propriedade da família em BTC.

## Hipótese (§1)

**Edge mean-reversion BTC 1h sobrevive janela temporal não-correlata.** I.2 (2025-H2) teve
hit 65.85%; J.2 (2024-H2) precisa cruzar 45%.

## Mercado (§2)

BTCUSDT spot, Binance Vision. Janela 2024-07-05 → 2024-12-31, 4320 barras 1h.

## Entradas (§4)

Idêntico a I.2 — ADR-0026, edge-triggered duplo, `window=20, num_std=2.0, long_only=True`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média (ADR-0026). Custos H.1.

## Critério de refutação

ADR-0025 híbrido.
