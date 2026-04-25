# SPEC.md — BK.1 bollinger 30/1.25 ETH 1h 2024-H1 + bollinger_width:250

> Gate: **pesquisa**. Série BK (sensitivity sweep em num_std).

## Hipótese

Perturbação ns=1.5 → 1.25 no combo-âncora ETH 2024-H1 do baseline v2. Bandas mais
estreitas geram mais sinais; se o Pareto aprovado é robusto, o Sharpe OOS deve
cair ≤ 30% e ainda passar strict gates (Sharpe ≥ 1.0, MDD ≤ 20%, PnL > 0, trades ≥ 30).

Se BK.1 passa, libera rollout paralelo dos outros 7 pilotos da série. Se falha,
investiga se ns=1.5 é ponto singular antes de seguir.

## Mercado

`ethusdt_1h_20240105_20240704_binance_spot`, ~4320 barras 1h. Mesmo dataset do baseline
AZ.1 — comparação lado-a-lado direta.

## Entradas

`BollingerMeanReversionStrategy(window=30, num_std=1.25)` causal, edge-triggered,
long_only + regime gate `bollinger_width:window=20:num_std=2.0:min_width_bps=250`
(inalterado vs baseline).

## Saídas

Edge-triggered mean-reversion (close[t-1] cruza acima da MA). Runtime-faithful:
entry/exit ambos `market_at_open_next_bar`, sizing `fixed_notional_per_trade`,
stop loss `disabled` (ADR-0030). Custos H.1: `taker_fee_bps=5`, `slippage_bps=10`.

## Critério

ADR-0025 híbrido + strict tail gate (p5 MC ≥ 10000). Além dos gates, registrar
Δ vs baseline (Sharpe, MDD, PnL, trades).

## Motivação BK vs AZ

AZ.1 validou ns=1.5 como ponto ótimo cross-window. BK.1 testa vizinho esquerdo
(ns=1.25) pra checar se o Pareto é largo. Se ns=1.25 também passa, ns=1.5 não é
overfit — é parte de uma região robusta.

## Contrato runtime-faithful

Este piloto declara aderência a ADR-0030. Qualquer manifest emitido daqui (caso
aprovado em handoff futuro) deve setar `runtime_contract: "faithful"` e os 5
invariantes explícitos — validado via `alpha_forge.exports.validate_manifest`
(ADR-0031).
