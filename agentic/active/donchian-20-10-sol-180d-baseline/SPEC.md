# SPEC.md — Donchian 20/10 SOLUSDT 1h 180d (H.10)

> Gate: **pesquisa**. Terceiro asset do protocolo (após H.2a ETH + H.9 ETH+SMA). Primeira exposição a SOL. **12° piloto agentic — marco do protocolo H**.

## Hipótese (§1)

**SOL tem volatilidade e dispersão fold-a-fold maior que BTC/ETH — hit_rate pode estar polarizado (alguns folds muito bons, outros muito ruins) em vez de estável em faixa 25-32%.** Se ao menos um fold cruzar 45%, confirma que filtros/regimes seriam ferramentas úteis em asset mais errático; se a distribuição fold-a-fold for tão polarizada que nem a agregada cruze, define limite mínimo de assets investigáveis por esta família Donchian.

## Mercado (§2)

SOLUSDT spot, Binance Vision.

## 3. Timeframe

1h OHLCV; 4320 barras; 2025-07-05 a 2025-12-31.

## Entradas (§4)

`ENTER_LONG` quando `close[t-1]` rompe `max(high[t-20..t-1])` — Donchian 20 long-only.

## Saídas (§5)

`EXIT` quando `close[t-1]` rompe `min(low[t-10..t-1])`. Idêntico a H.1 (BTC) e H.2a (ETH).

## 6-11-bis

Sem stops; `fracao=0.1, alav=2.0`; custos H.1; **sem filtro**.

## 12-13

Warm-up 20. Limitação: SOL historicamente mais volátil — drawdown máximo pode aproximar do piso de 35%.

## Critério de refutação

1. `hit_rate` baseline < 45%.
2. `max_drawdown` baseline > 35%.
3. `final_equity` `spread+10` / baseline < 0.95.

**Corroboração:** 3 passam AND `hit_rate fold máx > 45%` (qualquer fold cruza).

**Experimento controlado:** `compare` H.1 (BTC) ↔ H.10 (SOL) → 2 flags diff (`dataset_id`, `run_id`). `compare` H.2a (ETH baseline sem filter) ↔ H.10 → 2 flags diff idem.
