# SPEC.md — P.3 Bollinger 20/2 BTC 1h 2024 + composite AND

> Gate: **pesquisa**. Terceiro piloto Série P — composite AND (sma_slope + atr_regime)
> sobre J.2 BTC Bollinger. Testa se combinar filtros dá ganho adicional.

## Hipótese (§1)

**Combinação AND (`atr_regime` AND `sma_slope`) sobre J.2 BTC Bollinger
2024-H2 é mais restritiva que qualquer filtro puro e melhora MC p5 sem
degradar hit abaixo de P.2.** ADR-0023 `CompositeFilter`.

## Mercado (§2)

BTCUSDT spot, Binance Vision, 2024-07-05 → 2024-12-31, 4320 barras 1h.

## Entradas (§4)

Bollinger `window=20, num_std=2.0, long_only=True` + pre-filter
`and(atr_regime:window=14:min_atr_bps=50, sma_slope:window=50:min_slope_bps=10)`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média. Custos H.1.

## Critério de refutação

ADR-0025 híbrido.

## Família de filtro

`composite AND` (ADR-0023, primeira aplicação em Bollinger mean-reversion).
