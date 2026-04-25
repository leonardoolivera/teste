# 0184 — Série PY pré-reg: pyramid v4 aplicado a edges proven do stack

**Status:** Proposed
**Date:** 2026-04-21
**Deciders:** Usuário ("testa mais") + agente
**Relates to:** ADR-0180 (runtime v4 pyramid), ADR-0182 (CONS refuted), ADR-0140/0084 (SOL trendhtf baseline), ADR-0090 (SOL/BTC naked baselines)

## Hipótese testável

**Pyramid sizing amplifica edge já-provado OU o edge fixed_notional não sobrevive ao timing pyramid (signal ≠ sizing).**

Distinto de CONS (ADR-0181): CONS testou sinal novo (BB short consolidation) + sizing novo (pyramid) simultaneamente — refuta ambos sem decompor. PY **fixa o sinal** (RSI short já validado com Sh≥1.5 cross-era) e **varia só o sizing**. Decompõe a contribuição de v4 pyramid.

## Probes Fase 1 (3 runs cheap)

Todos reutilizam engines+filters dos manifests v3 faithful existentes, só trocam sizing.

| Tag | Sinal (de manifest existente) | Asset | Janela | Baseline Sh (fixed) | Baseline PnL% |
|---|---|---|---|---:|---:|
| PY.1 | RSI 14/25/75 short + trend_htf(4h/50/short_only) | SOL | 2025-H1 | 2.00 | 9.80 |
| PY.2 | RSI 14/30/70 short naked | SOL | 2025-H2 | 2.30 | 13.81 |
| PY.3 | RSI 14/30/70 short naked | BTC | 2025-H2 | 1.64 | 5.13 |

## Variáveis fixas

- **Sizing v4 pyramid**: `--sizing-mode pyramid_equity --pyramid-max-tranches 5 --pyramid-tranche-equity-frac 0.20 --pyramid-rearm-cooldown-bars 1 --alavancagem 5.0`
- **Custos**: fee_bps=5, slippage_bps=2 (idem resto)
- **Folds**: 4 rolling, train_fraction 0.5, min_test_bars 50
- **MC**: 1000 resamples, seed 42
- **Stress**: fee+10, spread+10

## Gate Fase 1

**Amplification test**: pyramid_Sh ≥ 1.5 AND seqs ≥ 10, **≥2/3 probes passando**.

Decomposição de resultados:
- **≥2/3 pass Sh≥1.5 AND Sh ≥ 0.9×baseline_Sh** → pyramid preserva edge → v4 viável como sizing alternativo
- **≥2/3 pass Sh≥1.5 mas Sh < 0.9×baseline_Sh** → pyramid degrada edge mas ainda passa gate → ambíguo, não promover
- **<2/3 Sh≥1.5** → pyramid não preserva edge → v4 rejeitado como paradigma geral

## Priors

Leverage 5× amplifica drawdown MTM. Baselines usam `notional_per_trade=2000` (20% equity × 1×lev). Pyramid 5×20%×5×lev = exposição máx 500% equity — 25× mais agressivo. Sh é scale-invariant para fixed sizing mas pyramid tem timing endógeno → Sh pode mover.

- P(≥2/3 pass AND preserva edge): **~20%** — leverage provavelmente degrada Sh mesmo em sinais bons
- P(≥2/3 pass mas degrada): **~25%** — passa padrão mínimo mas pior que baseline
- P(<2/3 pass): **~55%** — leverage mata edge apesar de signal proven

**Cenário "refutação específica" vs "refutação genérica"**: se PY.1 (filtrado) passa mas PY.2/PY.3 (naked) falham, hipótese = pyramid precisa filter protetor (trend_htf corta caudas, regime flip fecha stack). Se PY.2/PY.3 passam mas PY.1 falha, hipótese = pyramid prefere signals sem filter (naked mais trades = mais sequências pyramid).

## Não-alvo

- Não variar leverage nesta Fase 1 (fixa 5× conforme CONS/ADR-0181 para continuidade)
- Não testar outras assets/janelas antes de Fase 1 resolver
- Se Fase 1 passar: Fase 2 cross-era (6 runs) + variante leverage 2× para decomposição

## Ação planejada

1. Criar `tools/run_py_sweep.py` (3 runs)
2. Criar `tools/summarize_py.py` (gate check + lift vs baseline)
3. Rodar
4. ADR-0185 closeout (aprovar/refutar)
