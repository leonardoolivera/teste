# 0195 — Série TF10m pré-reg: BB+width short 10m cross-window × 3 ativos

**Status:** Accepted — probe em execução
**Date:** 2026-04-21
**Deciders:** Usuário (redirect pós-pausa 2 + ST) + agente
**Relates to:** ADR-0096 (snapshot), ADR-0177/0178 (TF15m), ADR-0179 (TF30m refutado), Padrão 44 (timeframe sweet spot), Padrão 46/47 (TF sweep exhaustion)

## Motivação

Usuário retomou séries pós-autopilot-pausa-2 e ST refutado pedindo **timeframe 10 minutos**. Binance Vision não publica 10m nativamente (grid: 1m/3m/5m/15m/30m/...). Resolvido via **resample local 5m→10m** (2 barras 5m consecutivas → 1 barra 10m OHLCV, origin=epoch).

Histórico TF:
- **1h** é o sweet spot comprovado (stack 13 combos).
- **4h** sepultado (Padrão 44, ADR-0096).
- **15m** refutado (ADR-0178, Padrão 46 — 9 runs, 0/9).
- **30m** refutado (ADR-0179, Padrão 47 timeframe — 9 runs, 0/9).
- **5m** nunca testado (noise/fees deveriam dominar; prior quase-zero).

**Gap lógico**: 10m está entre 5m (noise-heavy) e 15m (já refutado). Pode haver zona intermediária onde ruído per-trade cai o suficiente para sinal emergir, mas fees ainda não dominam. Prior: **muito pessimista** — mais provável que Padrão 46/47 se estenda para 10m (N=3 timeframes intra-hora refutados = padrão consistente contra intra-hour). Se passar em ≥1/9 setup semelhante a 15m/30m, merece investigação regime-específica; se 0/9, consolida Padrão 46 em âmbito "todo timeframe intra-hour refutado".

## Decisão (pré-reg)

**9 probes TF10.1–TF10.9**: Bollinger+width short 10m em 3 ativos × 3 janelas:

- **Engine**: `--strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --no-long-only`
- **Filter**: `--regime-filter bollinger_width:window=30:num_std=1.5:min_width_bps=250`
- **Ativos**: BTC, ETH, SOL
- **Janelas**: 2024-H2, 2025-H1, 2025-H2
- **Datasets**: `{btc,eth,sol}usdt_10m_<window>_binance_spot_resampled`
- **Costs/stress**: mesmo budget canônico (fees=5bps, slippage=2bps/notional, stress fee+10 e spread+10)
- **Folds**: 5 rolling, train 0.5, MC 1000 seed 42
- **Annualização Sharpe**: `sqrt(144 × 365) ≈ 229.25` (144 barras 10min/dia)

## Gate

**Gate mínimo (Padrão 41 analógico)**: ≥2/9 `annual_sharpe ≥ 1.5 AND trades ≥ 30`.

## Decisão condicional

- **Pass (≥2/9)**: considerar engine variação (RSI+width ou BB sem width) em 10m para confirmar se timeframe per se é o fator; só então pensar em promoção cross-era.
- **1/9**: Padrão 45 (outlier isolado), closeout.
- **0/9**: Padrão 46 **extendido formalmente** — "todo timeframe intra-hour refutado" (5m não testado mas 10m/15m/30m cobertos). Closeout + arquivamento da frente timeframes-mais-rápidos.

## Prior

**Muito pessimista.** 2 timeframes intra-hour já refutados em N=9 cada (18 runs, 0 promoções). A hipótese "10m é zona de transição" é concebível mas especulativa. Probabilidade de pass ≥2/9: **~10–15%**.

Custo de rodar baixo (infra pronta, dados cached), expected value do conhecimento (confirma ou refuta Padrão 46 extensão): alto.

## Integrity guard — resample

Datasets 10m são **derivados de 5m** (resample local, source tag `resampled_from:<source_id>` no manifest). Preserva invariantes OHLCV (open=first, high=max, low=min, close=last, volume=sum, origin=epoch, label=left). Gaps declarados herdados da fonte. Engine/backtest usa o parquet resampled sem distinção — todas as invariantes runtime (open@t+1, fixed_notional, exit_wins_on_tie) continuam válidas.

Se qualquer probe pass o gate, **re-validar** re-ingerindo 5m com novo hash antes de considerar export (source transparency).

## Não-alvo

- Não testar RSI+width 10m antes de ver BB+width (prior paralelo; economia de compute).
- Não testar long-only em 10m (engines approved de MR são direction-agnostic por design).
- Não tunar parâmetros 10m-specific (BB window=20, num_std=2.0, width min=250bps) antes do probe cego.
- Não testar 10m bollinger sem filter width (já sabemos que width é essencial via CZ-series).
- Não exportar manifest v4 pyramid nem compositar com CP/ST — refutados.
