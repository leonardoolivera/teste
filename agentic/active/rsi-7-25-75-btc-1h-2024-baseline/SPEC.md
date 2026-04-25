# SPEC.md — RSI 7/25/75 BTCUSDT 1h 2024-H2 (O.1)

> Gate: **pesquisa**. Primeiro piloto Série O — sweep de parâmetros RSI sobre
> BTC 1h 2024-H2 (asset onde N.2 teve maior convergência com Bollinger J.2).

## Hipótese (§1)

**Configuração RSI mais rápida + thresholds mais apertados (7/25/75) aumenta
edge via mais trades bons vs 14/30/70 padrão.** Refutação: custos cumulativos
derrubam `spread+10/baseline < 0.95` (mesmo mecanismo de Série L 15m).

## Mercado (§2)

BTCUSDT spot, Binance Vision. Janela 2024-07-05 → 2024-12-31
(`btcusdt_1h_20240705_20241231_binance_spot`).

## 3. Timeframe

1h OHLCV (sweet spot validado).

## Entradas (§4)

ADR-0027 com `period=7, oversold=25, overbought=75, long_only=True`. Período
menor → RSI reage mais rápido; oversold mais apertado → entra só em quedas
mais fortes.

## Saídas (§5)

Edge-triggered midline 50 (inalterado).

## 6–11-bis

Custos H.1 (5/2/0 bps); `fracao=0.1, alav=2.0`; sem stops/filtro.

## Critério de refutação (ADR-0025)

1. `hit_rate ≥ 45%`.
2. `max_drawdown ≤ 35%`.
3. `spread+10 / baseline ≥ 0.95` **← principal risco, dada frequência esperada maior**.

**Experimento controlado:** `compare` N.2 ↔ O.1 → flags diff em `rsi_period`,
`rsi_oversold`, `rsi_overbought`, `run_id`.
