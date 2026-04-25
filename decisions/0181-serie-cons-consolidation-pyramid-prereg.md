# 0181 — Série CONS pré-reg: consolidação + pyramid v4 Fase 1

**Status:** Proposed
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0180 (runtime v4 pyramid), ADR-0022 (regime filter), Padrão 41 (gate 2/3), Padrão 47 (diminishing returns)

## Hipótese

**Em regimes de consolidação (banda de Bollinger estreita em bps), mean reversion intra-range funciona se permitirmos escalar a posição progressivamente (pyramid) e sair imediatamente ao primeiro sinal de breakout (filtro de regime desativar).**

Racional:
- Todas as frentes cheap refutadas hoje (Keltner, zscore, BB+width 1h/15m/30m, TF menor) usavam filtro `min_width_bps` (HIGH vol). Ortogonal.
- Consolidação historicamente é o pior regime para breakout engines (Donchian whipsaw) mas **o melhor para oscilador mean-revert** dentro do range.
- Pyramid corrige sub-exposição natural do BB short em range: preço pode tocar banda superior 2-5 vezes antes de reverter, cada toque é uma tranche.
- Regime flip (banda expande acima do `max_width_bps`) = breakout provável = exit imediato antes do tail perder PnL.

## Frente CONS — variáveis fixas (não variar nesta série)

- **Strategy:** `bollinger` window=20 num_std=2.0 **short-side habilitada** (`--no-long-only`).
- **Timeframe:** `1h`.
- **Filter:** `bollinger_width:window=30:num_std=1.5:max_width_bps=200` (novo parâmetro opt-in; banda estreita).
- **Runtime contract:** `pyramid_equity_based` (ADR-0180).
- **Sizing:** `--tranche-equity-frac 0.20 --max-tranches 5 --alavancagem 5.0 --sizing-mode pyramid_equity`.
- **Rearm:** `--rearm-cooldown-bars 1` (1h bars LTF = 1h real).
- **Custos:** `--taker-fee-bps 5 --slippage-bps-per-notional 2` (iguais a toda a pesquisa).
- **Folds:** 5 rolling, train_fraction 0.5, min_test_bars 50, MC 1000 seed 42, stress fee+10 e spread+10.

## Probes Fase 1 (3 runs cheap, gate fast-fail)

| Tag | Dataset | Janela |
|---|---|---|
| CONS.1 | BTC 2025-H1 | 1h 2025-01-05 → 2025-07-04 |
| CONS.2 | ETH 2025-H1 | 1h 2025-01-05 → 2025-07-04 |
| CONS.3 | SOL 2025-H1 | 1h 2025-01-05 → 2025-07-04 |

## Gate de aprovação Fase 1

**Padrão 41 adaptado a v4-pyramid (ADR-0180 §approval gate):**
- OOS annual Sharpe ≥ 1.5
- **≥15 sequências de entrada distintas** cross-3-runs (não ≥30 trades — em pyramid 5 tranches = 1 seq). Relax para **≥10 sequências distintas** em Fase 1 single-era (gate completo cross-era é Fase 2).
- ≥2/3 ativos passando.

**Se Fase 1 passa** → Fase 2 cross-window (6 runs adicionais em 2024-H2 + 2025-H2) para validar Padrão 43 (asset + era).
**Se Fase 1 refuta** → closeout ADR-0182 + Padrão novo sobre consolidação no cripto + volta a autopilot pausa.

## Pré-dev necessário (ADR-0180 dependência)

Antes de rodar:
1. `BollingerWidthFilter` ganha `max_width_bps` opt-in (default `inf`).
2. Engine opt-in `pyramid_equity` via novo `SizingMode.PYRAMID_EQUITY` + stack `_Tranche`.
3. CLI flags novos: `--max-tranches`, `--tranche-equity-frac`, `--rearm-cooldown-bars`.
4. Tests unitários (filtros + engine pyramid stack/rearm/exit-all).
5. Manifest v4 schema (só se Fase 1 aprovar — aí paga o dev bot).

## Priors

- P(Fase 1 passa Sh≥1.5 em 2/3): **~30-40%**. Mean reversion em cripto historicamente funciona em janelas específicas; pyramid amplifica PnL se padrão existir mas amplifica drawdown se não existir.
- P(resultado viável mas não cross-era): **~25%**. Se Fase 1 passa mas Fase 2 refuta → Padrão novo "consolidação edge é era-específica em cripto".
- P(refutação total Fase 1): **~35-45%**. Se acontece, closeout imediato + pausa autopilot.

Este é o primeiro prior >30% desde o início da Série zscore — justifica o dev de ~2h.

## Não-alvo

- Não testar engines outros (RSI, donchian) em consolidação nesta série. Se CONS passar, variantes vão em Fase 3 separada.
- Não variar `tranche_equity_frac`, `max_tranches`, `rearm_cooldown_bars` em Fase 1. Testar variações só se Fase 2 aprovar.
- Não testar `max_atr_bps` como filter alternativo nesta série. Diferente hipótese — outra pré-reg se CONS refutar com `max_width_bps`.
- Não exportar manifest v4 até bot implementar runtime (flag `pending_runtime_impl: true` no ADR-0180).

## Próximos passos

1. Dev (filter + engine + CLI + tests) — hoje.
2. Rodar CONS.1-3.
3. Summarize + decisão (gate).
