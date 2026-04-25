# AUDIT.md - AF.3

> Gate: **auditoria**.

## Hipótese × evidência

SOL colapsa em 2025 (H1 fe 9770, H2 fe 9264) — ambos perdem capital. Asset instável OOS.

## Comparação cross-window

| Janela | hit | fe | decisão |
|--------|----:|---:|--------|
| 2024-H2 | 66.67% | 11210 | in-sample |
| 2025-H1 (este) | 58.14% | 9770.68 | canary_only |
| 2025-H2 | 46.67% | 9264 | canary (loss) |

**Padrão:** SOL colapsa em 2025 (66→58→47, ambos H1/H2 perdem capital)

## Blockers

Nenhum bloqueio técnico.

## Release

release_decision: `canary_only`

## ADR-0019

Stress fee+10 ≡ spread+10 = 9427.48.
