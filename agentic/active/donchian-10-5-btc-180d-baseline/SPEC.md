# SPEC.md — Donchian 10/5 BTCUSDT 1h 180d (H.7)

> Gate: **pesquisa**. Primeira variação de **hiperparâmetro de janela** do protocolo. Testa se o plateau 25-30% hit observado em H.1-H.6 é consequência da janela 20/10 ou da estratégia inteira.

## Hipótese (§1)

**Janela menor (10/5) captura micro-regimes que Donchian 20/10 perde.** Se o plateau for hiperparâmetro-dependente, H.7 deveria cruzar critério 1; se o plateau for estrutural (estratégia+dataset), janela menor apenas gera mais trades com mesmo hit_rate.

## Mercado (§2)

BTCUSDT spot, Binance Vision.

## 3. Timeframe

1h OHLCV; 4320 barras; 2025-07-05 a 2025-12-31.

## Entradas (§4)

`ENTER_LONG` quando `close[t-1]` rompe `max(high[t-10..t-1])`.

## Saídas (§5)

`EXIT` quando rompe `min(low[t-5..t-1])`.

## 6-10. Stops / Sizing / Fees / Slippage / Spread

Idênticos a H.1. Sem stops; `fracao=0.1, alavancagem=2.0`; `taker_fee_bps=5`; `slip=2`; `spread=0`.

## 11. Funding

N/A — spot.

## 11-bis. Regime filter

Nenhum (`none`).

## 12-13. Warm-up / Limitações

Warm-up 10 barras. Limitação: janela curta aumenta trade_count → maior sensibilidade a custos.

## Critério de refutação

1. `hit_rate` baseline < 45%.
2. `max_drawdown` baseline > 35%.
3. `final_equity` `spread+10` / baseline < 0.95.

**Critério de corroboração:** 3 passam AND `trade_count ≠ 110` (contra H.1).

**Experimento controlado:** `compare` H.1 ↔ H.7 deve mostrar 3 flags diff (`entry_window 20→10`, `exit_window 10→5`, `run_id`).
