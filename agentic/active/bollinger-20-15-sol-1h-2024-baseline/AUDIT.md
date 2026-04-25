# AUDIT.md - AE.4

> Gate: **auditoria**.

## Hipótese × evidência

Hipótese: 20/1.5 tem edge in-sample 2024 em SOL.

**Resultado:** controle SOL sem filtro: hit 64.96% fe 10872 — 20/1.5 supera 20/2 em SOL 2024 mesmo sem filtro (comparar R.1 sem filtro J.1=10684)

## Comparação cross-window (IN-SAMPLE vs OOS)

- AE.4 2024 (SOL): hit 64.96% fe 10872.74
- Série AD (2025, mesmo config se aplicável): edge degrada ou perde.

**Implicação:** parametrização 20/1.5 **tem edge in-sample em 3 assets** (BTC, ETH, SOL em 2024). Degradação em AD é **cross-window**, não asset-specific puro. ETH parece mais robusto cross-window; BTC/SOL degradam mais.

## Blockers

Nenhum bloqueio técnico.

## Release

release_decision: `canary_only`

## ADR-0019

Stress fee+10 ≡ spread+10 = 10403.48.
