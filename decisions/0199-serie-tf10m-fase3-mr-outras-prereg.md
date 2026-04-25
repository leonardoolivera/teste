# 0199 — Série TF10m Fase 3 pré-reg: outras MR strategies em 10m (zscore, Keltner, composite)

**Status:** Accepted — probe em execução
**Date:** 2026-04-21
**Deciders:** Usuário ("tenta reversao a media outras estrategias") + agente
**Relates to:** ADR-0198 (Fase 2 closeout + Padrão 46 consolidado), ADR-0170/0175/0189 (canonical Keltner/zscore/composite), Padrão 46/48

## Motivação

Após Fase 2 refutada (ADR-0198 consolidando Padrão 46 sobre BB/RSI × long/short × width/trend_htf em 10m/15m/30m), user pediu **testar outras MR strategies em 10m**. MR engines disponíveis no alpha_forge não cobertas em Fase 1/2:

| Strategy | Status histórico | Canonical params |
|---|---|---|
| zscore | ADR-0175 1h, ADR-0176 refutado cross-era | window=20, threshold=2.0 |
| keltner | ADR-0170-0174 1h, refutado | window=20, atr_period=14, mult=2.0 |
| composite_bb_rsi | ADR-0189, Padrão 49 candidato | bb_window=20, ns=2.0, rsi period=14, 30/70 |

Total: 9 + 9 + 9 = **27 probes**.

## Decisão (pré-reg)

### Bloco F — zscore MR 10m (TF10F.1-9)
- `--strategy zscore --no-long-only --zscore-window 20 --zscore-threshold 2.0`
- BTC/ETH/SOL × 2024-H2 / 2025-H1 / 2025-H2
- Sem regime filter (teste naked, igual ADR-0175 original 1h).

### Bloco G — Keltner MR 10m (TF10G.1-9)
- `--strategy keltner --no-long-only --keltner-window 20 --keltner-atr-period 14 --keltner-mult 2.0`
- BTC/ETH/SOL × 2024-H2 / 2025-H1 / 2025-H2
- Sem regime filter (teste naked, igual ADR-0170 original 1h).

### Bloco H — composite_bb_rsi 10m (TF10H.1-9)
- `--strategy composite_bb_rsi --no-long-only --composite-bb-window 20 --composite-bb-num-std 2.0 --composite-rsi-period 14 --composite-rsi-oversold 30 --composite-rsi-overbought 70`
- BTC/ETH/SOL × 2024-H2 / 2025-H1 / 2025-H2
- Sem regime filter (composite já é AND de 2 condições, naked é baseline canônica).

Config comum: capital=10k, fracao=0.1, alavancagem=2, fees=5bps, slippage=2bps/notional, folds=5 rolling, train=0.5, MC=1000 seed=42, stress fee+10 e spread+10.

Annualização Sharpe: `sqrt(144 × 365) ≈ 229.25`.

## Gate

**Gate por bloco**: ≥2/9 `annual_sharpe ≥ 1.5 AND trades ≥ 30`.

**Gate agregado Fase 3**: ≥2/27 probes passing (threshold paralelo Fase 2, matching noise floor).

## Decisão condicional

- **Algum bloco ≥2/9**: promove engine MR específica para validação cross-era 10m densa antes de pensar em extension do stack.
- **Todos blocos 0-1/N pass**: Padrão 46 consolida **além BB/RSI** — toda MR intra-hour refuta cross-window cross-asset cross-engine. Closeout Fase 3 + arquivamento definitivo frente MR 10m.
- **Passers novamente concentrados em SOL 2024-H2**: reforça Padrão 48 expandido (regime window-specific), não promove.

## Prior

**Muito pessimista.** Fase 1+2 refutaram BB/RSI; zscore/Keltner refutados em 1h (não faria sentido terem edge em 10m se não têm em 1h, dado padrão "1h sweet spot" ADR-0198). Composite é AND de BB+RSI que individualmente falham em 10m — prior ainda menor.

- Prior de qualquer bloco individual ≥2/9: **~10%**.
- Prior agregado Fase 3 ≥2/27 passing: **~20%** (isolated outliers mais prováveis que cluster).
- Prior de passers clusterizados em SOL 2024-H2 (Padrão 48 expand): **~40% condicional em qualquer pass** (dado 3/3 pattern já observado Fase 1+2).

Valor informacional alto mesmo fail: **fecha MR 10m cross-engine completamente** (todas 5 MR disponíveis cobertas: BB, RSI, zscore, Keltner, composite). Após isso, MR 10m é exaustão definitiva, não extensível.

## Integrity guard

- Mesmos 9 datasets 10m resampled de Fase 1/2 (source tag `resampled_from:<5m-source-id>`).
- Mesmas invariantes runtime (open@t+1, fixed_notional, exit_wins_on_tie).
- Engines zscore/Keltner/composite já existem no código — nenhuma infra nova.

## Não-alvo

- Não testar supertrend/ma_crossover/donchian em 10m (não-MR ou refutados + prior ~0).
- Não tunar params zscore/Keltner/composite antes de probe cego (mesma disciplina ADR-0197).
- Não adicionar width regime filter a Fase 3 (desvia da canônica original 1h, seria outro experimento).
- Não rodar long-only/short-only isolados (probes já são symmetric MR; tunar direção é 2º experimento).
