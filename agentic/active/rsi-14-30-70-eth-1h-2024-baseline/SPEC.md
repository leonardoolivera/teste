# SPEC.md — RSI 14/30/70 ETHUSDT 1h 2024-H2 (N.3)

> Gate: **pesquisa**. Terceiro piloto Série N — fecha trio cross-asset RSI.

## Hipótese (§1)

**Se N.3 cruza os 3 critérios ADR-0025 em ETH 1h 2024-H2, Série N fecha 3/3
canary_only → edge MR 1h é estrutural cross-família + cross-asset + cross-window**
(6 pilotos validados: 3 Bollinger J + 3 RSI N). Refutação: N.3 falha → edge RSI
tem limite asset-específico.

## Mercado (§2)

ETHUSDT spot, Binance Vision. Janela 2024-07-05 → 2024-12-31 (mesmo dataset de
J.3: `ethusdt_1h_20240705_20241231_binance_spot`).

## 3. Timeframe

1h OHLCV.

## Entradas (§4)

ADR-0027 (`period=14, oversold=30, overbought=70, long_only=True`).

## Saídas (§5)

Edge-triggered midline 50 (conservador, não em overbought=70).

## 6–11-bis

Custos H.1; `fracao=0.1, alav=2.0`; sem stops/filtro.

## Critério de refutação (ADR-0025)

1. `hit_rate ≥ 45%`; 2. `mdd ≤ 35%`; 3. `spread+10/baseline ≥ 0.95`.
