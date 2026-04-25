# 0122 — Série CZ5 pré-registro: RSI short 4h cross-asset (BTC+ETH gap)

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0115 (CT closeout: SOL 4h replica forte, BTC misto), Padrão 28

## Motivação

CT.1-CT.3 cobriu SOL 4h 2025-H2 (strict 2.81), BTC 4h 2025-H1 width (0.77 fraca), BTC 4h 2025-H2 naked (FAIL -0.43). Padrão 28 = cross-timeframe é ativo-específica; falta evidence em ETH 4h (nunca testado) e BTC 4h 2024-H2.

Hipótese: se ETH 4h replica como SOL, temos base para stack 4h multi-asset. Se só SOL replica, reforça Padrão 28.

## Escopo

4 runs, RSI(14/30/70) short naked, 4h:

| Tag | Asset | Janela | Regime |
|---|---|---|---|
| CZ5.1 | BTC | 2024-H2 | bull com chop |
| CZ5.2 | ETH | 2024-H2 | bull com chop |
| CZ5.3 | ETH | 2025-H1 | chop |
| CZ5.4 | ETH | 2025-H2 | misto |

## Gate pré-registrado

Por asset (trades ≥ 15, Padrão 30):
- **ETH replica forte**: ≥2/3 ETH Sh ≥ 1.0 → ETH 4h RSI short vira candidato manifest v9-4h-multiasset
- **ETH replica parcial**: 1/3 ETH Sh ≥ 1.0 → staging contextual single-asset-single-window
- **ETH refutado**: 0/3 ETH Sh ≥ 0.5 → RSI short 4h é SOL-específico, Padrão 28 reforçado

BTC 2024-H2 (CZ5.1): isolado, apenas fecha a matriz BTC (3/3 janelas 4h).

Timebox: ~8min wall. Closeout em ADR-0123.
