# SPEC.md — Bollinger 20/2 SOL 4h 2024 (M.1)

> Gate: **pesquisa**. Primeiro da Série M — direção oposta de L (4h em vez de 15m).
> Série L falhou por custos (15m multiplica trades → custos engolem edge); M testa
> se timeframe maior preserva edge com menos trades.

## Hipótese (§1)

**Em 4h, critério 3 (spread+10/baseline) deve passar folgado** (poucos trades, pouca
exposição a custos). Pergunta aberta: **edge estatístico sobrevive à redução de
frequência de sinal?**

## Mercado (§2)

SOLUSDT spot, Binance Vision. 2024-07-05 → 2024-12-31, **1080 barras 4h** (¼ de 1h).

## Entradas (§4)

ADR-0026 edge-triggered duplo, `window=20, num_std=2.0, long_only=True`.

## Saídas (§5)

Edge-triggered duplo em cruzamento de média. Custos H.1.

## Critério de refutação

ADR-0025 híbrido. Esperado: critério 3 passa folgado; risco é critério 1 (hit≥45%)
com amostra pequena.
