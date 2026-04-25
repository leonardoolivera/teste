# 0178 — Série TF closeout: Bollinger+width 15m refutado cross-window

**Status:** Accepted — 15m como timeframe arquivado para BB+width.
**Date:** 2026-04-20
**Deciders:** Usuário (piloto automático) + agente
**Relates to:** ADR-0177 (pré-reg), Padrão 44 (timeframe), Padrão 46 (novo)

## Resultado consolidado

9 runs (3 ativos × 3 janelas semestrais), mesma config `bollinger+width 20/2.0 short 15m`:

| Tag | Dataset | Trades | Sharpe | PnL% | Pass |
|---|---|---:|---:|---:|:---:|
| TF.1 | BTC 2024-H2 | 39 | 1.19 | 1.49 | ❌ (< 1.5) |
| TF.2 | ETH 2024-H2 | 61 | **1.61** | 3.03 | ✅ |
| TF.3 | SOL 2024-H2 | 111 | **2.03** | 6.83 | ✅ |
| TF.4 | BTC 2025-H1 | 34 | **1.80** | 2.68 | ✅ |
| TF.5 | ETH 2025-H1 | 99 | -3.45 | -11.50 | ❌ |
| TF.6 | SOL 2025-H1 | 132 | -0.96 | -4.42 | ❌ |
| TF.7 | BTC 2025-H2 | 25 | 1.02 | 1.08 | ❌ |
| TF.8 | ETH 2025-H2 | 76 | -1.62 | -4.10 | ❌ |
| TF.9 | SOL 2025-H2 | 115 | -1.23 | -4.54 | ❌ |

**Fase 1 (2024-H2): 2/3 pass.** **Fase 2 cross-window (2025-H1+H2): 1/6 pass.** **Total 9 runs: 3/9.**

## Interpretação

### Inversão completa ETH/SOL 2024 → 2025

| Ativo | 2024-H2 | 2025-H1 | 2025-H2 |
|---|---:|---:|---:|
| BTC | 1.19 | **1.80** | 1.02 |
| ETH | **1.61** | -3.45 | -1.62 |
| SOL | **2.03** | -0.96 | -1.23 |

ETH e SOL **inverteram sinal** (positivo → fortemente negativo). BTC é único consistente (média ~1.3 mas <1.5 em 2/3). Classicamente edge era-específico de **2024-H2**: bear-consolidation favorável para short MR; 2025 bull-trend destrói short MR em timeframe rápido.

### Por que 15m falha onde 1h funciona em 2025

BB+width 1h 2025-H1/H2 é base do stack aprovado (BK/BN/BO). Em 15m, mesma estratégia **falha** nos mesmos ativos/janelas. Hipóteses:

1. **Slippage+fees não-lineares**: 15m gera ~4× trades (ETH 99 vs ~25 em 1h). Cada trade paga 10bps taker + spread — em 15m os custos consomem parte do edge que em 1h sobrevive.
2. **Signal/noise**: banda 15m toca com frequência sem reversão significativa. Filter `bollinger_width:min_width_bps=250` foi calibrado para 1h; em 15m width-events são menores e mais ruidosos.
3. **Regime dependency**: 2024-H2 teve vol consolidada com reversões rápidas (favorável 15m); 2025 bull-trend dá false-signals em short.

Todos 3 plausíveis, não decomponíveis sem mais runs. Refutação via Padrão 43 (diversity falha) + Padrão 46 (edge timeframe+era-específico).

## Padrão 46 (novo) — Edge era-específico em timeframe menor

**Enunciado**: Uma estratégia que passa gate Padrão 41 em timeframe T0 (ex: 1h) pode falhar em timeframe T0/4 (ex: 15m) **mesmo em janelas onde T0 passa**, porque a redução de timeframe amplifica custos relativos e ruído, tornando o edge era-específico.

**Evidência**: BB+width 1h 2025-H1/H2 passa ETH e SOL (no stack aprovado); BB+width 15m 2025-H1/H2 dá Sh=-3.45/-1.62 para ETH e -0.96/-1.23 para SOL (mesmos ativos+janelas).

**Diferença vs Padrão 44 (4h sepultado)**: Padrão 44 é sobre timeframe maior com trades sparse insuficientes. Padrão 46 é sobre timeframe menor com trades abundantes mas edge cross-era instável.

**Implicação**: nunca assumir que edge em 1h implica edge em 15m/30m — revalidar desde o zero.

## Decisão

- **BB+width 15m arquivado.** Não promover.
- Frente "timeframes alternativos com engines aprovadas" **parcialmente exaurida** — só 15m testado, 30m não ingerido.
- **Autopilot pausado** após 3 refutações consecutivas (Keltner, zscore, TF 15m). Todas as frentes cheap-probe testadas:
  - ✅ Novos engines (2 tentados, 2 refutados)
  - ✅ Timeframes alternativos (15m refutado)
  - ⏸️ BB+RSI composite engine (requer dev CLI novo)
  - ⏸️ Portfolio/cross-sectional engine (requer dev substancial)
  - ⏸️ 30m (requer ingest + run ~15min)

## Próximo passo

Antes de arquivar definitivo o autopilot, **uma última frente cheap**: testar **30m BB+width** com 3 janelas (2024-H2, 2025-H1, 2025-H2) — ~9 runs, custo ingest+compute ~20min total. Hipótese: 30m pode ser sweet spot entre 1h (edge bom) e 15m (refutado). Prior: pessimista, mas custo baixo.

Se 30m falhar = autopilot declara frentes cheap exauridas → pausa formal aguardando direção user.

## Não-alvo

- Não tunar params 15m (window=30, threshold diferente) — prior muito fraco após refutação 3/9
- Não testar RSI 15m antes de decidir 30m BB (prior paralelo, mesma expectativa)
- Não tentar filter diferente em 15m (width foi canônico; mudar filter é overfitting)
