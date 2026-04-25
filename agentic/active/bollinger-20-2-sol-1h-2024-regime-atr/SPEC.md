# SPEC.md — Q.1 Bollinger 20/2 SOL 1h 2024 + atr_regime

> Gate: **pesquisa**. Primeiro piloto Série Q — replicação cross-asset do filtro
> dominante da Série P. Hipótese: ganho do `atr_regime` em BTC (P.2) generaliza
> para outros assets mean-reversion 1h 2024-H2.

## Hipótese (§1)

**Filtro `atr_regime:14:50` sobre J.1 SOL Bollinger 2024-H2 melhora hit baseline
ou fe sem degradar critério 3.** Replicar P.2 em SOL para validar universalidade
do ganho do filtro ATR.

## Mercado (§2)

SOLUSDT spot, Binance Vision, 2024-07-05 → 2024-12-31, 4320 barras 1h
(dataset idêntico a J.1).

## Entradas (§4)

Bollinger `window=20, num_std=2.0, long_only=True` + pre-filter
`atr_regime:window=14:min_atr_bps=50` (ADR-0022).

## Saídas (§5)

Edge-triggered duplo em cruzamento de média (ADR-0026). Custos H.1.

## Critério de refutação

ADR-0025 híbrido.

## Família de filtro

`atr_regime` replicando P.2 configuração exata.
