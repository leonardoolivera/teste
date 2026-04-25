# AUDIT.md - AE.2

> Gate: **auditoria**.

## Hipótese × evidência

Hipótese: 20/1.5 tem edge in-sample 2024 em SOL.

**Resultado:** fe 11210 é MELHOR fe do protocolo (supera R.1 SOL 20/2 fe=10803); 20/1.5 é superior a 20/2 em SOL 2024

## Comparação cross-window (IN-SAMPLE vs OOS)

- AE.2 2024 (SOL): hit 66.67% fe 11210.74
- Série AD (2025, mesmo config se aplicável): edge degrada ou perde.

**Implicação:** parametrização 20/1.5 **tem edge in-sample em 3 assets** (BTC, ETH, SOL em 2024). Degradação em AD é **cross-window**, não asset-specific puro. ETH parece mais robusto cross-window; BTC/SOL degradam mais.

## Blockers

Nenhum bloqueio técnico.

## Release

release_decision: `canary_only`

## ADR-0019

Stress fee+10 ≡ spread+10 = 10824.71.
