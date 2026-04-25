# SPEC.md — RSI 14/30/70 SOLUSDT 1h 2024-H2 (N.1)

> Gate: **pesquisa**. Primeiro piloto Série N — segunda família mean-reversion
> (RSI, ADR-0027), mesma janela 2024-H2 1h da Série J. Discrimina se edge é
> estrutural a mean-reversion no regime 1h ou era Bollinger-específico.

## Hipótese (§1)

**Se RSI mean-reversion cruza os 3 critérios ADR-0025 em 2024-H2 no regime 1h, o
edge é estrutural a mean-reversion (não Bollinger-específico).** Se RSI falha
onde Bollinger passou (Série J: 3/3 canary_only), edge é assinatura da família
Bollinger — famílias MR não são intercambiáveis.

## Mercado (§2)

SOLUSDT spot, Binance Vision. Janela 2024-07-05 → 2024-12-31, 4320 barras 1h.
**Mesmo dataset de J.1** (`solusdt_1h_20240705_20241231_binance_spot`) — controle
cross-família.

## 3. Timeframe

1h OHLCV. Sweet spot formalizado pelas Séries L (15m quebra) + M (4h quebra).

## Entradas (§4)

ADR-0027, edge-triggered em cruzamento estrito de `oversold=30`:
`rsi_now < 30 AND rsi_prev >= 30` → `ENTER_LONG`. SMA smoothing (não Wilder),
`period=14`, `long_only=True`.

## Saídas (§5)

Edge-triggered em cruzamento estrito de `midline=50`:
`rsi_now >= 50 AND rsi_prev < 50` → `EXIT` (não em overbought=70, conservador).

## 6–11-bis

Custos H.1 (5/2/0 bps); `fracao=0.1, alav=2.0`; sem stops; sem filtro de regime.

## Critério de refutação (ADR-0025)

1. `hit_rate baseline ≥ 45%`.
2. `max_drawdown ≤ 35%`.
3. `spread+10 / baseline ≥ 0.95`.
4. Rank top-3 para `paper_only`.

**Experimento controlado:** `compare` J.1 ↔ N.1 → 2 flags diff (`strategy`,
`rsi_*` vs `bollinger_*`, mesmo `dataset_id`/`run_id` só no nome).
