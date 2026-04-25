# SPEC.md — Donchian 20/10 BTCUSDT 1h 180d + regime filter SMA slope (H.3)

> Gate ativo: **pesquisa**. Estratégia e filtro já existem em código (ADR-0011 + ADR-0022); este piloto exercita o **primeiro consumidor real** de ADR-0022 sobre configuração baseline (H.1) + `--regime-filter sma_slope:window=50:min_slope_bps=10`. Gap zero em `src/`.

## Hipótese (§1)

**Regime é a causa raiz das 4 refutações anteriores.** Se um filtro causal de *slope da SMA* aplicado antes de `Strategy.decide` suprime sinais em regimes não-tendenciais, então a **Donchian breakout long-only** com janelas `entry_window=20` / `exit_window=10`, operando sobre **BTCUSDT 1h 180d** com custos idênticos ao piloto H.1 (fee 5bps taker + slippage 2bps/unit_notional + spread 0bps), **recupera edge** — `hit_rate ≥ 45%` e `final_equity ≥ 0.95 × capital_inicial`, condições que H.1 violou (`hit_rate = 25.45%`, `final_equity = 9089.79`).

Refrasando afirmativamente: "em 180 dias de BTC 1h, um trader que compra em rompimento de 20-barras e vende em rompimento-baixo de 10-barras, **apenas quando o slope da SMA-50 excede 10 bps em módulo**, termina com equity maior que 0.95 × capital inicial e hit_rate ≥ 45%".

Refutação desta hipótese significa que o recorte específico "slope SMA-50 ≥ 10 bps" não é o regime correto (mas a arquitetura ADR-0022 está validada para próximas iterações — RSI, ATR, HMM, etc.). Corroboração significa que o filtro de regime é suficiente para mover o sistema acima do limiar de edge.

## Mercado (§2)

- **Ativo:** BTCUSDT (spot, venue = Binance Vision dumps — público).
- **Regime do período (observado):** BTC em consolidação de alta → lateral → baixa. Expectativa: filtro SMA-slope deve suprimir os períodos laterais/de reversão, concentrando sinais em tendências direcionais claras.

## 3. Timeframe

- **Grão:** 1 hora (1h OHLCV).
- **Período total:** 2025-07-05 00:00 UTC a 2025-12-31 23:00 UTC (~180 dias, 4320 barras). **Idêntico a H.1.**

## Entradas (§4)

`ENTER_LONG` emitido quando `close[t-1]` rompe `max(high[t-20..t-1])` — **coagido a `HOLD` se** `regime_filter.is_active(window) == False` (ADR-0022). Filtro lê apenas `window.iloc[:-1]`, causal por construção.

## Saídas (§5)

`EXIT` emitido quando `close[t-1]` rompe `min(low[t-10..t-1])` para baixo. **Coerção adicional (ADR-0022):** se o regime desativar enquanto posicionado, engine força `EXIT` imediato (t+1 open, com custo de saída normal ADR-0006).

## 6. Stops

Sem stops explícitos. Saída só acontece por (a) rompimento-baixo de 10-barras OU (b) desativação do filtro de regime.

## 7. Sizing

Idêntico a H.1: `fixed_fractional_position_sizing` com `fracao=0.1`, `alavancagem=2.0` → notional = **2000 USDT**.

## 8. Fees

Idêntico a H.1: `taker_fee_bps = 5.0`.

## 9. Slippage

Idêntico a H.1: `slippage_bps_per_unit_notional = 2.0` → slip efetivo ≈ **0.4 bps** por fill.

## 10. Spread (ADR-0019)

`spread_bps = 0.0` no baseline. Sensibilidade testada via `cost_stress` com `spread+10:0:0:10`.

## 11. Funding

N/A — spot.

## 11-bis. Regime filter (ADR-0022)

`SMASlopeFilter(window=50, min_slope_bps=10.0)`:

- `causal = window.iloc[:-1]` (ignora barra `t` — ADR-0002 herdado).
- `sma = causal["close"].rolling(50).mean()`.
- `slope_bps = (sma.iloc[-1] - sma.iloc[-51]) / sma.iloc[-51] * 10000`.
- **Ativo** quando `abs(slope_bps) >= 10`. Warm-up (`len(causal) < 51`) retorna `False`.

Canonicalização em `run.json`: `flags["regime_filter"] == "sma_slope:min_slope_bps=10:window=50"` (ordem alfabética).

## 12. Condições inválidas

- Warm-up: primeiras `max(entry_window=20, sma_window + 1 = 51) = 51` barras produzem `HOLD` por construção (filtro retorna `False` + estratégia em warm-up).
- `close[t-1]` com valor `NaN`: dataset declara `declared_gaps: []` — sem gaps.
- Short side: `long_only=True` (idêntico a H.1).

## 13. Limitações conhecidas

- **Um único filtro testado.** `sma_slope:window=50:min_slope_bps=10` é a configuração de estreia; variações (`window ∈ {20, 100, 200}`, `min_slope_bps ∈ {5, 20, 50}`) ficam para pilotos posteriores.
- Dataset único BTCUSDT — cross-asset ETH/SOL com regime filter fica para H.4+.
- Janela 180d continua curta para trend-following; regime filter pode ser *ainda mais restritivo* que o necessário e suprimir sinais legítimos.
- Sem tuning de `min_slope_bps` (valor 10 bps escolhido por inspeção, não por grid search — ADR-0003 proíbe tuning dentro do walk-forward).

## Critério de refutação (explícito e auditável)

O piloto é **refutado** (`release_decision = fail`) se qualquer uma das três condições for observada na validação:

1. `hit_rate` do baseline cost_stress (4320 barras) **< 45%**.
2. `max_drawdown` do baseline **> 35%**.
3. `final_equity` do cenário `spread+10:0:0:10` **< 95% do baseline** (delta vs baseline < -5%).

**Critério de corroboração (interpretação positiva):** todas as 3 condições passam AND `trade_count < trade_count(H.1) = 110` (filtro deve reduzir sinais, não manter ou aumentar).

**Experimento controlado:** `alpha-forge compare donchian-20-10-btc-180d-baseline donchian-20-10-btc-180d-regime-sma` deve mostrar exatamente 2 flags divergentes (`regime_filter` e `run_id`). Qualquer outro diff em flags indica erro de configuração e invalida o piloto.
