# 0118 — Série CZ2 pré-registro: SOL RSI short 4h cross-window replicação

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0115 (CT.3 SOL 2025-H2 4h PASS Sh=2.81), Padrão 28

## Motivação

CT.3 (ADR-0115) mostrou SOL RSI short 4h 2025-H2 com Sh=2.81 (replica forte o baseline 1h 2.30). Probe único — precisa cross-window pra decidir se abre manifest paralelo v9-4h ou se é window-specific (Padrão 25).

## Escopo

2 runs, RSI(14/30/70) short naked, SOL 4h:

| Tag | Janela | Regime |
|---|---|---|
| CZ2.1 | 2024-H2 | bull com chop interno |
| CZ2.2 | 2025-H1 | chop |

Baseline CT.3: SOL 2025-H2 misto Sh=2.81, 23 trades.

## Gates pré-registrados

Agregado (baseline CT.3 + 2 janelas adicionais):
- **Promoção v9-4h**: ≥2/3 janelas com Sh ≥ 1.0 + trades ≥ 15 → abrir ADR-0120 manifest paralelo
- **Staging/contextual**: 1 adicional Sh ≥ 0.5 (2 janelas total com Sh ≥ 0.5) → candidato staging, não stack ativo
- **Refutação**: ambas janelas Sh < 0.5 → CT.3 era window-specific (Padrão 25 bloqueia)

Trades relaxado para 15 (sample natural menor em 4h — CT.3 teve 23).

## Expectativa

SOL em 2024-H2 é bull: RSI short histórico FAIL em bull (v6 ADR-0084 trend_htf rescue foi necessária). Hipótese base: CZ2.1 2024-H2 FAIL (sem trend filter), CZ2.2 2025-H1 incerto.

Se CZ2.2 2025-H1 PASS → staging (2/3 incluindo CT.3). Se também 2024-H2 PASS → promoção.

Timebox: 2 runs ~5min wall. ADR-0119 closeout.
