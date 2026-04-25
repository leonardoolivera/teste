# AUDIT.md - AF.1

> Gate: **auditoria**.

## Hipótese × evidência

BTC 2025-H1 PRESERVA edge (hit 58% fe 10360). 2025-H2 degrada (hit 44%). Decay gradual cross-window.

## Comparação cross-window

| Janela | hit | fe | decisão |
|--------|----:|---:|--------|
| 2024-H2 | 72.62% | 10474 | in-sample |
| 2025-H1 (este) | 58.21% | 10360.46 | canary_only |
| 2025-H2 | 44.44% | 9985 | fail |

**Padrão:** BTC decay contínuo 72→58→44 (17pp/semestre)

## Blockers

Nenhum bloqueio técnico.

## Release

release_decision: `canary_only`

## ADR-0019

Stress fee+10 ≡ spread+10 = 10092.02.
