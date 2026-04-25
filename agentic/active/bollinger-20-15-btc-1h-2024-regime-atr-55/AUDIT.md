# AUDIT.md - AE.1

> Gate: **auditoria**.

## Hipótese × evidência

Hipótese: 20/1.5 tem edge in-sample 2024 em BTC.

**Resultado:** hit 72.62% excelente; fe 10474 > baseline (AE.3 10178); 20/1.5 + filtro supera baseline BTC 2024

## Comparação cross-window (IN-SAMPLE vs OOS)

- AE.1 2024 (BTC): hit 72.62% fe 10474.48
- Série AD (2025, mesmo config se aplicável): edge degrada ou perde.

**Implicação:** parametrização 20/1.5 **tem edge in-sample em 3 assets** (BTC, ETH, SOL em 2024). Degradação em AD é **cross-window**, não asset-specific puro. ETH parece mais robusto cross-window; BTC/SOL degradam mais.

## Blockers

Nenhum bloqueio técnico.

## Release

release_decision: `canary_only`

## ADR-0019

Stress fee+10 ≡ spread+10 = 10137.88.
