# SPEC.md — Donchian 20/10 BTCUSDT 1h 180d + CompositeFilter(sma_slope OR atr_regime) (H.6)

> Gate: **pesquisa**. Segundo consumidor real de ADR-0023, modo `or`. Primeiro teste de CompositeFilter no modo permissivo após H.5 (modo restritivo AND) refutar.

## Hipótese (§1)

**Regime é multi-dimensional mas inclusivo: direção OR volatilidade recuperam edge que cada filtro isolado violou.** A simetria lógica com H.5 (AND) isola a **semântica de composição**: se AND (intersecção de bons regimes) refutou por filtrar demais (74 trades, hit 29.73%) e OR (união) também refutar com métricas piores, confirma que **nenhum subconjunto booleano dos filtros heurísticos disponíveis tem edge** — a família inteira está saturada.

Refrasando: "em 180 dias de BTC 1h, um trader Donchian 20/10 long-only que **aceita entrar quando SMA slope ≥ 10 bps OU ATR ≥ 50 bps** (união) termina com `hit_rate ≥ 45%` e `final_equity ≥ 0.95 × capital`".

## Mercado (§2)

BTCUSDT spot, Binance Vision — idêntico a H.1/H.3/H.4/H.5.

## 3. Timeframe

1h OHLCV; 2025-07-05 00:00 UTC a 2025-12-31 23:00 UTC (4320 barras).

## Entradas (§4)

`ENTER_LONG` quando rompe Donchian 20, coagido a `HOLD` se `or(sma, atr).is_active(window) == False`. OR retorna `True` quando **pelo menos um** dos filtros retorna `True` — mais permissivo que cada individual.

## Saídas (§5)

`EXIT` quando rompe Donchian 10-baixo, OU quando **ambos** filtros caírem (OR `False` força EXIT se posicionado).

## 6. Stops

Sem stops explícitos.

## 7. Sizing

`fracao=0.1, alavancagem=2.0` → notional 2000 USDT.

## 8. Fees

`taker_fee_bps = 5.0`.

## 9. Slippage

`slippage_bps_per_unit_notional = 2.0`.

## 10. Spread

`spread_bps = 0.0` baseline; stress `spread+10`.

## 11. Funding

N/A — spot.

## 11-bis. Regime filter (ADR-0022 + ADR-0023)

`CompositeFilter([SMASlopeFilter(50, 10), ATRRegimeFilter(14, 50)], mode="or")`:

- Warm-up efetivo: `max(51, 15) = 51 barras causais`.
- Canonical: `or(atr_regime:min_atr_bps=50:window=14,sma_slope:min_slope_bps=10:window=50)`.

## 12. Condições inválidas / 13. Limitações

Idênticas a H.5. Expectativa: trade_count maior que H.3 (114) e H.4 (72) — OR é permissivo; se cair abaixo de H.3, sinal de bug.

## Critério de refutação

Piloto **refutado** se qualquer:

1. `hit_rate` baseline < 45%.
2. `max_drawdown` baseline > 35%.
3. `final_equity` `spread+10` / baseline < 0.95.

**Critério de corroboração:** 3 passam AND `trade_count > 114` (OR deve ser mais permissivo que cada individual — contraparte ADR-0023 property 2 a nível de signal-emission).

**Experimento controlado:** `compare` H.5 ↔ H.6 deve mostrar 2 flags diff (`regime_filter` com `and → or`).
