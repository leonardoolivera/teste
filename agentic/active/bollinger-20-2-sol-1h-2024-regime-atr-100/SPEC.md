# SPEC.md — R.1 Bollinger 20/2 SOL 1h 2024 + atr_regime:100

> Gate: **pesquisa**. Primeiro piloto Série R — calibração de threshold ATR
> por asset. Hipótese: Q.1 falhou em gerar ganho em SOL porque threshold 50
> bps é baixo demais para asset high-vol; threshold calibrado pode reativar.

## Hipótese (§1)

**Filtro `atr_regime:14:100` (threshold 2× maior que P.2 BTC) sobre J.1 SOL
Bollinger 2024-H2 reativa filtro e domina Q.1 e J.1 em métricas operacionais.**

## Mercado (§2)

SOLUSDT spot, Binance Vision, 2024-07-05 → 2024-12-31, 4320 barras 1h.

## Entradas (§4)

Bollinger `window=20, num_std=2.0, long_only=True` + pre-filter
`atr_regime:window=14:min_atr_bps=100` (ADR-0022, threshold dobrado).

## Saídas (§5)

Edge-triggered duplo em cruzamento de média. Custos H.1.

## Critério de refutação

ADR-0025 híbrido.

## Família de filtro

`atr_regime` com threshold calibrado por asset (primeiro piloto com threshold
diferente de 50).
