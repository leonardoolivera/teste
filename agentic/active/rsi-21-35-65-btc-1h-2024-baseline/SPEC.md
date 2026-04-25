# SPEC.md — RSI 21/35/65 BTCUSDT 1h 2024-H2 (O.2)

> Gate: **pesquisa**. Segundo piloto Série O — controle inverso de O.1. Período
> maior + thresholds mais largos → menos trades, menos sensível a custos.

## Hipótese (§1)

**Configuração mais lenta + thresholds mais largos preserva critério 3 com
menor trade-count, custa hit mais baixo.** Testa extremo oposto de O.1 para
mapear sensibilidade paramétrica.

## Mercado (§2)

BTCUSDT spot. Janela 2024-07-05 → 2024-12-31
(`btcusdt_1h_20240705_20241231_binance_spot`).

## 3. Timeframe

1h OHLCV.

## Entradas (§4)

ADR-0027 com `period=21, oversold=35, overbought=65, long_only=True`.

## Saídas (§5)

Edge-triggered midline 50.

## 6–11-bis

Custos H.1; `fracao=0.1, alav=2.0`; sem stops/filtro.

## Critério de refutação (ADR-0025)

1. `hit_rate ≥ 45%`.
2. `max_drawdown ≤ 35%`.
3. `spread+10 / baseline ≥ 0.95` (esperado passar por folga).

**Experimento controlado:** trio N.2 ↔ O.1 ↔ O.2 mapeia sensibilidade
paramétrica RSI em BTC 2024-H2.
