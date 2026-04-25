# SPEC.md — S.1 RSI 14/30/70 BTC 1h 2024 + atr_regime:50

> Gate: **pesquisa**. Piloto Série S — cross-family transfer (filtro
> ATR sobre RSI mean-reversion, não Bollinger).

## Hipótese (§1)

**Filtro `atr_regime:14:50` generaliza cross-family: se é safe/valioso
em Bollinger (P.2, Q.1, Q.2, R.1), também deve agregar em RSI
mean-reversion (N.2 BTC baseline).**

## Mercado (§2)

BTCUSDT spot, Binance Vision, 2024-07-05 → 2024-12-31, 4320 barras 1h
(mesmo dataset H.1/P/N.2).

## Entradas (§4)

RSI `period=14, oversold=30, overbought=70` (ADR-0027) + pre-filter
`atr_regime:window=14:min_atr_bps=50`.

## Saídas (§5)

Edge-triggered cruzamento médio. Custos H.1.

## Critério de refutação

ADR-0025 híbrido.

## Família de filtro

`atr_regime` aplicado cross-family (RSI em vez de Bollinger). Testa se
valor do filtro é específico da família ou universal.
