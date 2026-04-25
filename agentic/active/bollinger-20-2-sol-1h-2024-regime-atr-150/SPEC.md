# SPEC.md — R.2 Bollinger 20/2 SOL 1h 2024 + atr_regime:150

> Gate: **pesquisa**. Segundo piloto Série R — threshold extremo para mapear
> curva de utilidade.

## Hipótese (§1)

**Filtro `atr_regime:14:150` (threshold 3× maior que P.2 BTC) sobre J.1 SOL
Bollinger 2024-H2 é over-filtering — corta muitos sinais válidos, amostra
final pequena, edge instável.**

## Mercado (§2)

SOLUSDT spot, Binance Vision, 2024-07-05 → 2024-12-31, 4320 barras 1h.

## Entradas (§4)

Bollinger `window=20, num_std=2.0, long_only=True` + pre-filter
`atr_regime:window=14:min_atr_bps=150`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média. Custos H.1.

## Critério de refutação

ADR-0025 híbrido.

## Família de filtro

`atr_regime` com threshold propositalmente extremo (mapeamento de curva).
