# SPEC.md — Bollinger 20/1.5 SOL 180d 2024 (K.1)

> Gate: **pesquisa**. Primeiro da Série K — sensibilidade ao hiperparâmetro `num_std`.
> Testa banda mais estreita (1.5σ) sobre SOL 2024 (melhor tape do protocolo).

## Hipótese (§1)

**Se o edge é robusto, uma banda mais estreita (`num_std=1.5`) não deve colapsar o hit_rate.**
Variação ∈ [1.5, 2.0, 2.5] na dimensão de threshold de reversão.

## Mercado (§2)

SOLUSDT spot 2024-07-05 → 2024-12-31, 4320 barras 1h.

## Entradas (§4)

ADR-0026 edge-triggered duplo, `window=20, num_std=1.5, long_only=True`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média. Custos H.1.

## Critério de refutação

ADR-0025 híbrido. Se hit colapsa (<45%), edge é sensível a threshold de banda — red flag.
