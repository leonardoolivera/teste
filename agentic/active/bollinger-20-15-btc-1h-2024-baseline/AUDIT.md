# AUDIT.md - AE.3

> Gate: **auditoria**.

## Hipótese × evidência

Hipótese: 20/1.5 tem edge in-sample 2024 em BTC.

**Resultado:** controle BTC sem filtro: hit 65.09% fe 10178 — 20/1.5 tem edge próprio em BTC 2024 (comparar com AE.1 para isolar ganho do filtro: +7.5pp hit, +296 fe)

## Comparação cross-window (IN-SAMPLE vs OOS)

- AE.3 2024 (BTC): hit 65.09% fe 10178.86
- Série AD (2025, mesmo config se aplicável): edge degrada ou perde.

**Implicação:** parametrização 20/1.5 **tem edge in-sample em 3 assets** (BTC, ETH, SOL em 2024). Degradação em AD é **cross-window**, não asset-specific puro. ETH parece mais robusto cross-window; BTC/SOL degradam mais.

## Blockers

Nenhum bloqueio técnico.

## Release

release_decision: `canary_only`

## ADR-0019

Stress fee+10 ≡ spread+10 = 9754.93.
