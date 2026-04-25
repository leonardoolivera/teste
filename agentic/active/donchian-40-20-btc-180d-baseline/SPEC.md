# SPEC.md — Donchian 40/20 BTCUSDT 1h 180d (H.8)

> Gate: **pesquisa**. Complementa H.7 na exploração de janela — mesma estratégia, mesma asset, janela **maior** (40/20 vs 10/5 vs 20/10 default).

## Hipótese (§1)

**Janela maior captura apenas macro-regimes, reduz custos via menor trade_count, preserva ou melhora hit_rate.** Se o plateau for devido a "excesso de sinais ruidosos", janela maior deveria filtrar ruído e cruzar 45%. Se o plateau for estrutural, janela maior apenas reduz frequência sem mover hit.

## Mercado (§2)

BTCUSDT spot, Binance Vision.

## 3. Timeframe

1h OHLCV; 4320 barras.

## Entradas (§4)

`ENTER_LONG` quando `close[t-1]` rompe `max(high[t-40..t-1])`.

## Saídas (§5)

`EXIT` quando `close[t-1]` rompe `min(low[t-20..t-1])`.

## 6-11-bis

Idênticos a H.1. Nenhum filtro; `fracao=0.1, alav=2.0`; custos padrão.

## 12. Warm-up

40 barras (janela entry).

## 13. Limitações

Com 4320 barras e trade_count ~40-60 esperado, power estatístico de hit_rate cai — fold_count será decisivo.

## Critério de refutação

1. `hit_rate` baseline < 45%.
2. `max_drawdown` baseline > 35%.
3. `final_equity` `spread+10` / baseline < 0.95.

**Corroboração:** 3 passam AND `trade_count < 110` (H.1).

**Experimento controlado:** `compare` H.1 ↔ H.8 → 3 flags diff (`entry_window`, `exit_window`, `run_id`).
