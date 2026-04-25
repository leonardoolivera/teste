# SPEC.md — Donchian 20/10 ETHUSDT 1h 180d + SMASlopeFilter (H.9)

> Gate: **pesquisa**. **Primeiro cross-asset com filtro.** Testa se o plateau hit~30% é universal ou restrito a BTC — se ETH + SMA filter cruzar 45% onde BTC+SMA (H.3) não cruzou, confirma que asset é dimensão crítica.

## Hipótese (§1)

**ETH tem edge residual que BTC não tem para Donchian 20/10 + SMA filter.** Intuição: ETH em 2025-07→12-31 teve mais volatilidade direcional (ETF aprovação, upgrade networks); SMA slope filter pode capturar melhor nessa dinâmica.

## Mercado (§2)

ETHUSDT spot, Binance Vision.

## 3. Timeframe

1h OHLCV; 4320 barras; 2025-07-05 a 2025-12-31.

## Entradas (§4)

`ENTER_LONG` rompe Donchian 20, coagido a `HOLD` se `sma_slope(50, 10)` falso.

## Saídas (§5)

`EXIT` rompe Donchian 10-baixo, OU SMA slope cai abaixo de 10 bps.

## 6-10

Sem stops; `fracao=0.1, alav=2.0`; `fee=5, slip=2, spread=0`.

## 11. Funding

N/A — spot.

## 11-bis. Regime filter

`SMASlopeFilter(window=50, min_slope_bps=10)` — idêntico a H.3 (BTC+SMA). Warm-up 51.

## 12-13

Warm-up 51 (SMA domina). Limitação: um asset, um período, mesma família de estratégia — só isola *asset* como variável independente.

## Critério de refutação

1. `hit_rate` baseline < 45%.
2. `max_drawdown` baseline > 35%.
3. `final_equity` `spread+10` / baseline < 0.95.

**Corroboração:** 3 passam AND `final_equity > 10000` (breakeven absoluto — ETH historicamente gerou mais alpha que BTC).

**Experimento controlado:** `compare` H.3 (BTC+SMA) ↔ H.9 (ETH+SMA) → 2 flags diff (`dataset_id`, `run_id`) — isola exatamente asset.
