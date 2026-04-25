# SPEC.md — Donchian 20/10 BTCUSDT 1h 180d + CompositeFilter(sma_slope AND atr_regime) (H.5)

> Gate ativo: **pesquisa**. Primeiro consumidor real de ADR-0023 (CompositeFilter). Combina os filtros de H.3 e H.4 com AND lógico — teste direto da hipótese "regime é multi-dimensional (direção AND volatilidade)".

## Hipótese (§1)

**Regime é multi-dimensional: direção AND volatilidade juntas.** H.3 (`sma_slope`) maximiza centro da distribuição MC; H.4 (`atr_regime`) maximiza cauda inferior + reduz custos. Se **ambas as condições precisam ser verdadeiras** para que Donchian breakout tenha edge, então o AND composto deve atingir `hit_rate ≥ 45%` e preservar `final_equity ≥ 0.95 × capital_inicial`, condições que cada filtro isolado violou (H.1 25.45%, H.3 29.82%, H.4 26.39%).

Refrasando: "em 180 dias de BTC 1h, um trader que compra em rompimento de 20-barras e vende em rompimento-baixo de 10-barras, **apenas quando a SMA-50 está em tendência (slope ≥ 10 bps) E o ATR-14 é alto (≥ 50 bps normalizado)**, termina com equity ≥ 0.95 × capital inicial e hit_rate ≥ 45%".

Refutação significa: (a) os recortes específicos (slope ≥ 10 AND ATR ≥ 50) estão desalinhados, ou (b) a hipótese multi-dimensional AND está errada — filtros causais heurísticos são insuficientes sobre este dataset (abre caminho para HMM/ML na Frente H.6+). Corroboração valida ADR-0022+0023 como contrato suficiente e encerra a série H em 6 pilotos.

## Mercado (§2)

- **Ativo:** BTCUSDT spot, Binance Vision.
- **Regime observado:** consolidação → lateral → baixa.

## 3. Timeframe

- 1h OHLCV; 2025-07-05 00:00 UTC a 2025-12-31 23:00 UTC (4320 barras). Idêntico a H.1/H.3/H.4.

## Entradas (§4)

`ENTER_LONG` quando `close[t-1]` rompe `max(high[t-20..t-1])` — **coagido a `HOLD` se** `CompositeFilter.is_active(window) == False`. O composto retorna `True` apenas quando **ambos** `sma_slope` e `atr_regime` retornam `True`.

## Saídas (§5)

`EXIT` quando `close[t-1]` rompe `min(low[t-10..t-1])`. Coerção adicional: se SMA slope cair abaixo de 10 bps OU ATR cair abaixo de 50 bps enquanto posicionado, engine força `EXIT`.

## 6. Stops

Sem stops explícitos.

## 7. Sizing

`fracao=0.1, alavancagem=2.0` → notional 2000 USDT.

## 8. Fees

`taker_fee_bps = 5.0`.

## 9. Slippage

`slippage_bps_per_unit_notional = 2.0`.

## 10. Spread

`spread_bps = 0.0` baseline; stress `spread+10:0:0:10`.

## 11. Funding

N/A — spot.

## 11-bis. Regime filter (ADR-0022 + ADR-0023)

`CompositeFilter(filters=[SMASlopeFilter(window=50, min_slope_bps=10), ATRRegimeFilter(window=14, min_atr_bps=50)], mode="and")`:

- `is_active(window)` = `sma.is_active(window) AND atr.is_active(window)`.
- Warm-up: `max(SMA warmup, ATR warmup) = max(51, 15) = 51 barras causais`. Com Donchian warm-up (20), o gargalo efetivo é o SMA interno.
- Canonicalização: `flags["regime_filter"] = "and(atr_regime:min_atr_bps=50:window=14,sma_slope:min_slope_bps=10:window=50)"` (ordem lexicográfica; `atr_regime` antes de `sma_slope`).

**Escolha de parâmetros:** reuso exato de H.3 e H.4 — nenhum tuning. Testa hipótese composta sem mexer nos recortes que já foram definidos por inspeção.

## 12. Condições inválidas

- Warm-up: primeiras 51 barras produzem `HOLD` (SMA-50 + 1 exigindo 51 causais).
- `close[t-1]` NaN: dataset declara `declared_gaps: []`.
- Short side: `long_only=True`.

## 13. Limitações

- **Um único par testado** — variações (ex.: AND entre `atr_regime` com `min_atr_bps=100` + `sma_slope`) ficam para H.5b se justificado.
- Dataset único BTCUSDT; janela 180d.
- AND é conservador: resultado esperado é trade_count drasticamente menor que H.4 (já mais restritivo de todos). Se trade_count cair abaixo de ~30, power estatístico de hit_rate vira ruído — usar fold_count e hit_rate fold-a-fold para inspeção qualitativa.
- Sem tuning de thresholds — ADR-0003.

## Critério de refutação

Piloto **refutado** se qualquer:

1. `hit_rate` baseline cost_stress < 45%.
2. `max_drawdown` baseline > 35%.
3. `final_equity` de `spread+10` < 95% do baseline.

**Critério de corroboração:** 3 condições passam AND `trade_count < 72` (trade_count de H.4 — AND deve ser mais restritivo que cada filtro individual, validado por property-based ADR-0023).

**Experimento controlado triplo:**

- `compare` H.1 ↔ H.5: 2 flags diff.
- `compare` H.3 ↔ H.5: 2 flags diff (`regime_filter` com valores distintos).
- `compare` H.4 ↔ H.5: 2 flags diff (idem).

Todos os três devem mostrar exatamente 2 flags diff.
