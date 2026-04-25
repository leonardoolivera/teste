# SPEC.md — P.2 Bollinger 20/2 BTC 1h 2024 + atr_regime

> Gate: **pesquisa**. Segundo piloto Série P — família de filtro de volatilidade
> (ATR) sobre J.2 BTC Bollinger. Hipótese: mean-reversion é mais confiável em
> regime de volatilidade > threshold.

## Hipótese (§1)

**Filtro `atr_regime` (window=14, min_atr_bps=50) sobre J.2 BTC Bollinger
2024-H2 melhora hit baseline e MC p5 ao suprimir sinais em regime de baixa
volatilidade (onde bandas Bollinger são estreitas demais para edge real).**

## Mercado (§2)

BTCUSDT spot, Binance Vision, 2024-07-05 → 2024-12-31, 4320 barras 1h
(dataset idêntico a J.2/P.1).

## Entradas (§4)

Bollinger `window=20, num_std=2.0, long_only=True` (ADR-0026 inalterado)
+ pre-filter `atr_regime:window=14:min_atr_bps=50` (ADR-0022).

## Saídas (§5)

Edge-triggered duplo em cruzamento de média (ADR-0026). Custos H.1.

## Critério de refutação

ADR-0025 híbrido.

## Família de filtro

`atr_regime` (ADR-0022 segunda família, unidimensional magnitude).
