# SPEC.md — P.1 Bollinger 20/2 BTC 1h 2024 + sma_slope regime

> Gate: **pesquisa**. Primeiro piloto Série P — regime filter sobre J.2 BTC Bollinger.
> Dimensão ortogonal a parâmetros; infraestrutura pronta (ADR-0022).

## Hipótese (§1)

**Filtro `sma_slope` (window=50, min_slope_bps=10) sobre J.2 BTC Bollinger 2024-H2
melhora MC p5 sem degradar hit baseline mais de 3 pp.** ADR-0022 filtra
sinais quando mercado está em regime de trend fraco, hipótese de mean-reversion
é mais válida em regime lateral/reversão.

## Mercado (§2)

BTCUSDT spot, Binance Vision, 2024-07-05 → 2024-12-31, 4320 barras 1h
(dataset idêntico a J.2/N.2/O.1/O.2).

## Entradas (§4)

Bollinger `window=20, num_std=2.0, long_only=True` (ADR-0026 inalterado)
+ pre-filter `sma_slope:window=50:min_slope_bps=10` (ADR-0022).

## Saídas (§5)

Edge-triggered duplo em cruzamento de média (ADR-0026). Custos H.1
(5/2/0 bps). Custo duplo em reversões preservado.

## Critério de refutação

ADR-0025 híbrido — 3 critérios absolutos.

## Família de filtro

`sma_slope` (ADR-0022 primeira família, unidimensional direcional).
