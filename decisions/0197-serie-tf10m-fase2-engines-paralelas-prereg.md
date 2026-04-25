# 0197 — Série TF10m Fase 2 pré-reg: engines paralelas às do stack em 10m

**Status:** Accepted — probe em execução
**Date:** 2026-04-21
**Deciders:** Usuário ("testar em todas as outras" pós Fase 1 refutada) + agente
**Relates to:** ADR-0195/0196 (TF10m Fase 1 BB+width short), Padrão 46 extendido, ADR-0096 (stack snapshot)

## Motivação

Após TF10m Fase 1 refutada (BB+width short 1/9), usuário pediu testar **em todas as outras engines/combos**. Exhaustão do frente TF10m exige cobrir as 4 famílias restantes do stack em 10m:

| Engine | Stack fonte | Direction | Canonical params |
|---|---|---|---|
| BB long + width | v2 bollinger_width_regime | long | window=30, ns=1.5, filter width=250/1.5/30 |
| RSI short + width | v3 rsi_short_width | short | period=14, 30/70, filter width=250/1.5/30 |
| RSI long + width | v7 rsi_long_width_eth_2024h2 | long | idem (mirror de short) |
| RSI short + trend_htf | v6 rsi_short_trendhtf_sol | short (SOL only) | period=14, 25/75, filter trend_htf 4h/50/short_only |

Total: 9 + 9 + 9 + 3 (SOL × 3 windows) = **30 probes**.

Excluídos: zscore (não está no stack, refutado em ADR-0176 cross-era decay), Donchian/MACX/Keltner/supertrend/composite (todos refutados).

## Decisão (pré-reg)

**30 probes** cobertura completa TF10m Fase 2:

### Bloco A — RSI+width short (TF10B.1-9)
- `--strategy rsi --no-long-only --rsi-period 14 --rsi-oversold 30 --rsi-overbought 70`
- `--regime-filter bollinger_width:window=30:num_std=1.5:min_width_bps=250`
- BTC/ETH/SOL × 2024-H2 / 2025-H1 / 2025-H2

### Bloco B — BB+width long (TF10C.1-9)
- `--strategy bollinger --long-only --bollinger-window 30 --bollinger-num-std 1.5`
- filter idem
- BTC/ETH/SOL × 2024-H2 / 2025-H1 / 2025-H2

### Bloco C — RSI+width long (TF10D.1-9)
- `--strategy rsi --long-only --rsi-period 14 --rsi-oversold 30 --rsi-overbought 70`
- filter idem
- BTC/ETH/SOL × 2024-H2 / 2025-H1 / 2025-H2

### Bloco D — RSI+trend_htf short SOL (TF10E.1-3)
- `--strategy rsi --no-long-only --rsi-period 14 --rsi-oversold 25 --rsi-overbought 75`
- `--regime-filter trend_htf:htf=4h:sma_window=50:mode=short_only`
- SOL × 2024-H2 / 2025-H1 / 2025-H2

Config comum: capital=10k, fracao=0.1, alavancagem=2, fees=5bps, slippage=2bps/notional, folds=5 rolling, MC=1000 seed=42, stress fee+10 e spread+10.

Annualização Sharpe: `sqrt(144 × 365) ≈ 229.25`.

## Gate

**Gate por bloco**: ≥2/9 `annual_sharpe ≥ 1.5 AND trades ≥ 30` (≥1/3 para Bloco D que é SOL only).

**Gate agregado Fase 2**: ≥2/30 probes passing (threshold paralelo ao Fase 1 1/9 isolado).

## Decisão condicional

- **≥2 probes pass em mesmo bloco**: promove aquele engine para validação cross-era 10m mais densa antes de pensar em export.
- **Todos blocos 0-1/N pass**: Padrão 46 consolida **totalmente** para intra-hour (todas engines do stack × 10m refutadas). Total intra-hour: 10m/15m/30m × todas engines relevantes. Closeout Fase 2 + arquivamento definitivo.
- **1/N em múltiplos blocos mas sem ≥2 em algum**: Padrão 45 (outliers dispersos), closeout.

## Prior

**Muito pessimista.** Padrão 46 formalizado em ADR-0196 cobrindo BB+width short nos 3 intra-hour TFs. Extender para outras engines reforça a hipótese "noise+fees dominam em intra-hour", invariantes das engines MR. Prior de qualquer bloco passar gate ≥2/9: **~10%**. Prior agregado Fase 2 ≥2/30 passing: **~20-25%** (isolated outlier mais provável que cluster).

Valor informacional alto mesmo fail: fecha o capítulo TF10m definitivamente antes de considerar 5m (prior ~0) ou direções completamente diferentes (portfolio/microstructure).

## Integrity guard

- Mesmos datasets 10m resampled de Fase 1 (source tag `resampled_from:<5m-source-id>`).
- Mesmas invariantes runtime (open@t+1, fixed_notional, exit_wins_on_tie).
- Bloco D usa trend_htf 4h HTF: verificar resample HTF funciona com LTF 10m (deve — o filtro resampla via pandas com freq canônica, agnóstico ao LTF de origem).

## Não-alvo

- Não testar zscore/Keltner/Donchian em 10m (já refutados em 1h).
- Não testar engines/filters não ativos no stack (pyramid v4 refutado, composite CP refutado, supertrend ST refutado).
- Não tunar parâmetros engine-specific em 10m antes de probe cego.
- Não rodar BB short 20/1.5 (variação de Fase 1 que usou 20/2.0) — prior idêntico, marginal info.
