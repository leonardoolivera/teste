# SPEC.md — Donchian 20/10 BTCUSDT 1h 180d + regime filter ATR (H.4)

> Gate ativo: **pesquisa**. Segundo consumidor real de ADR-0022 (primeiro: H.3 com `sma_slope`). Mesma configuração baseline (H.1) + `--regime-filter atr_regime:window=14:min_atr_bps=50`. Gap de código mínimo: extensão aditiva de `src/alpha_forge/regimes/filter.py` com `ATRRegimeFilter` + 2 property-based + 1 integration CLI (pre-autorizada em ADR-0022 §Consequences → Positive: "novos filtros sem nova ADR").

## Hipótese (§1)

**Regime de volatilidade é a causa raiz das refutações, não regime de direção.** H.3 provou que `SMASlopeFilter` (direção de tendência) desloca distribuição +160 USDT sem cruzar breakeven. Se o problema não é "comprar na tendência" mas "evitar compressão/squeeze onde breakouts são whipsaws", então um filtro de **ATR normalizado** (volatilidade recente) aplicado antes de `Strategy.decide` deve **recuperar edge onde H.3 falhou** — `hit_rate ≥ 45%` e `final_equity ≥ 0.95 × capital_inicial`, condições que H.1 e H.3 violaram.

Refrasando afirmativamente: "em 180 dias de BTC 1h, um trader que compra em rompimento de 20-barras e vende em rompimento-baixo de 10-barras, **apenas quando ATR(14) normalizado pelo close supera 50 bps**, termina com equity maior que 0.95 × capital inicial e hit_rate ≥ 45%".

Refutação significa que nem regime de direção (`sma_slope`) nem regime de volatilidade (`atr_regime`) com os recortes testados são suficientes — causa raiz pode ser combinada (slope + vol), mais complexa (HMM), ou estrutural (janela 180d insuficiente, Donchian-family intrinsecamente frágil em BTC 1h). Corroboração significa que **família de filtro de regime importa**: volatilidade é o eixo dominante; arquitetura ADR-0022 é validada como contrato genérico real.

## Mercado (§2)

- **Ativo:** BTCUSDT spot, venue Binance Vision (público).
- **Regime do período observado:** julho 2025 → dezembro 2025 cobre consolidação de alta → lateral → baixa. Expectativa: filtro ATR-50bps suprime fases comprimidas (lateral baixa-vol) e ativa em fases direcionais (alta ou queda com range largo).

## 3. Timeframe

- **Grão:** 1h OHLCV.
- **Período:** 2025-07-05 00:00 UTC a 2025-12-31 23:00 UTC (4320 barras). Idêntico a H.1 e H.3.

## Entradas (§4)

`ENTER_LONG` quando `close[t-1]` rompe `max(high[t-20..t-1])` — **coagido a `HOLD` se** `regime_filter.is_active(window) == False` (ADR-0022). Filtro ATR lê `window.iloc[:-1]`, causal por construção.

## Saídas (§5)

`EXIT` quando `close[t-1]` rompe `min(low[t-10..t-1])`. **Coerção adicional (ADR-0022):** se ATR cair abaixo de 50bps enquanto posicionado, engine força `EXIT` em t+1 open.

## 6. Stops

Sem stops explícitos.

## 7. Sizing

`fixed_fractional_position_sizing(fracao=0.1, alavancagem=2.0)` → notional = 2000 USDT.

## 8. Fees

`taker_fee_bps = 5.0`.

## 9. Slippage

`slippage_bps_per_unit_notional = 2.0`.

## 10. Spread (ADR-0019)

`spread_bps = 0.0` baseline. Stress `cost_stress` com `spread+10:0:0:10`.

## 11. Funding

N/A — spot.

## 11-bis. Regime filter (ADR-0022)

`ATRRegimeFilter(window=14, min_atr_bps=50.0)`:

- `causal = window.iloc[:-1]`.
- `tr[i] = max(high[i]-low[i], |high[i]-close[i-1]|, |low[i]-close[i-1]|)` para `i in causal[-14:]`.
- `atr = mean(tr[-14:])`.
- `atr_bps = atr / close_causal[-1] * 10000`.
- **Ativo** quando `atr_bps >= 50`. Warm-up (`len(causal) < 15`) retorna `False`.

Canonicalização em `run.json`: `flags["regime_filter"] == "atr_regime:min_atr_bps=50:window=14"`.

**Escolha dos parâmetros:** `window=14` é o default clássico de Wilder para ATR em estudos de momentum; `min_atr_bps=50` foi escolhido por inspeção do dataset (50 bps ≈ 0.5% range médio por barra em BTC 1h, valor que separa aproximadamente o terço superior de volatilidade das fases comprimidas). Nenhum tuning dentro do walk-forward (ADR-0003).

## 12. Condições inválidas

- Warm-up: primeiras `max(entry_window=20, atr_window + 1 = 15) = 20` barras produzem `HOLD` por warm-up da estratégia + filtro. ATR specifically exige 15 barras causais; Donchian 20. O maior dos dois é Donchian.
- `close[t-1]` NaN: dataset declara `declared_gaps: []`.
- Short side: `long_only=True`.

## 13. Limitações conhecidas

- **Um único parâmetro de ATR testado** — `window=14, min_atr_bps=50`. Variações ficam para H.4b+ se H.4 corroborar.
- Dataset único BTCUSDT.
- Janela 180d continua curta.
- Sem tuning de `min_atr_bps` — ADR-0003.

## Critério de refutação

Piloto **refutado** se qualquer uma das três condições:

1. `hit_rate` do baseline cost_stress < 45%.
2. `max_drawdown` do baseline > 35%.
3. `final_equity` de `spread+10:0:0:10` < 95% do baseline (Δ < −5%).

**Critério de corroboração:** 3 condições passam AND `trade_count < 114` (trade_count de H.3 com `sma_slope`; filtro ATR deve ser **mais restritivo** no sentido de reduzir entradas, não só redistribuir).

**Experimento controlado:**

- `alpha-forge compare donchian-20-10-btc-180d-baseline donchian-20-10-btc-180d-regime-atr` → exatamente 2 flags divergentes (`regime_filter`, `run_id`).
- `alpha-forge compare donchian-20-10-btc-180d-regime-sma donchian-20-10-btc-180d-regime-atr` → exatamente 2 flags divergentes (`regime_filter`, `run_id`) — **primeiro uso protocolar de `compare` entre dois pilotos com filtro ativo**. Diferença métrica atribuível à família de filtro.
