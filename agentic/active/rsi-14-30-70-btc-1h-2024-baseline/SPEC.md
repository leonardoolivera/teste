# SPEC.md — RSI 14/30/70 BTCUSDT 1h 2024-H2 (N.2)

> Gate: **pesquisa**. Segundo piloto Série N. Controle cross-asset (BTC) da
> hipótese "edge MR 1h é estrutural, não Bollinger-específico".

## Hipótese (§1)

**Se N.2 cruza os 3 critérios ADR-0025 em BTC 1h 2024-H2, edge RSI replica no
asset onde J.2 Bollinger também cruzou** — MR@1h vira propriedade cross-família
+ cross-asset. Refutação: N.2 falha → edge RSI pode ser SOL-específico.

## Mercado (§2)

BTCUSDT spot, Binance Vision. Janela 2024-07-05 → 2024-12-31 (mesmo dataset de
J.2: `btcusdt_1h_20240705_20241231_binance_spot`).

## 3. Timeframe

1h OHLCV. Sweet spot formalizado (Séries L+M).

## Entradas (§4)

ADR-0027, edge-triggered `oversold=30`, `period=14`, `long_only=True`.

## Saídas (§5)

Edge-triggered `midline=50` (conservador).

## 6–11-bis

Custos H.1 (5/2/0 bps); `fracao=0.1, alav=2.0`; sem stops; sem filtro.

## Critério de refutação (ADR-0025)

1. `hit_rate baseline ≥ 45%`.
2. `max_drawdown ≤ 35%`.
3. `spread+10 / baseline ≥ 0.95`.

**Experimento controlado:** `compare` J.2 ↔ N.2 → flags diff só em `strategy`
+ `rsi_*` / `bollinger_*`.
