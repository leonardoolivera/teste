# 0167 — Série DE pré-reg: trend_htf 1d em RSI short 1h (cross-timeframe variant)

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário ("cross time frame + nova engine") + agente
**Relates to:** Padrão 40 (cross-era), Padrão 41 (janela-específica), ADR-0140 (trend_htf 4h canônico)

## Hipótese

Filter `trend_htf` foi canonizado com `htf=4h, sma_window=50` (RSI short combos SOL/BTC etc). Variante `htf=1d` nunca foi testada em engine 1h (só em engine 4h em CZ4/CZ4b, que foi sepultado). 1d é timeframe natural para bias macro cripto — pode selecionar regimes mais fortes que 4h.

Custo: 3 runs. Se passa gate, cross-window em 2025-H2 (3 runs adicionais).

## Probes (3 runs Fase 1)

Assets: combos RSI short canônicos 2025-H1.

| Tag | Combo | Dataset | Baseline (trend_htf 4h) Sh |
|---|---|---|---:|
| DE.1 | RSI 30/70 + trend_htf(1d, sma=50) | BTC 2025-H1 | — (não há combo BTC trendhtf 4h live) |
| DE.2 | RSI 30/70 + trend_htf(1d, sma=50) | ETH 2025-H1 | — |
| DE.3 | RSI 25/75 + trend_htf(1d, sma=50) | SOL 2025-H1 | 2.00 (cz10.5 live) |

SMA=50 em htf=1d equivale a ~50 dias de média (~1.5 meses) — razoável para bias macro.

Bounds RSI 25/75 apenas para SOL (espelha combo live); BTC/ETH usam canônico 30/70.

## Gate pré-registrado

- **Upgrade convergente**: ≥2/3 Sh ≥ 1.5 AND trades ≥ 40 → Fase 2 (cross-window 2025-H2)
- **Signal divergente (Padrão 41)**: 1/3 Sh ≥ 1.5 → bloqueia
- **Refutação**: 0/3 → arquivar 1d em 1h

Se SOL supera 2.00 (baseline 4h), também abre questão de **upgrade** do combo live trendhtf SOL — ADR dedicado.

## Não-alvo

- Não testar SMA windows ≠ 50 (1-knob foco)
- Não testar htf=1W em 1h (CZ4b já refutou 1W em 4h; prior pessimista)
- Não misturar com filter AND

## Ação

- Script `tools/run_de_sweep.py`
- Closeout ADR-0168
