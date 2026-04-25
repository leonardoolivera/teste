# SPEC.md — Q.2 Bollinger 20/2 ETH 1h 2024 + atr_regime

> Gate: **pesquisa**. Segundo piloto Série Q — replicação cross-asset do filtro
> dominante da Série P.

## Hipótese (§1)

**Filtro `atr_regime:14:50` sobre J.3 ETH Bollinger 2024-H2 melhora hit
baseline e empurra fe > 10000 (J.3 é único Bollinger `canary_only` com fe
sub-capital; filtro tentaria corrigir).**

## Mercado (§2)

ETHUSDT spot, Binance Vision, 2024-07-05 → 2024-12-31, 4320 barras 1h.

## Entradas (§4)

Bollinger `window=20, num_std=2.0, long_only=True` + pre-filter
`atr_regime:window=14:min_atr_bps=50` (ADR-0022).

## Saídas (§5)

Edge-triggered duplo em cruzamento de média. Custos H.1.

## Critério de refutação

ADR-0025 híbrido.

## Família de filtro

`atr_regime` replicando P.2 configuração exata.
