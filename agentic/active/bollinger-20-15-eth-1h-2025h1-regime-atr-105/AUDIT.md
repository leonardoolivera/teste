# AUDIT.md - AF.2

> Gate: **auditoria**.

## Hipótese × evidência

ETH é MAIS estável cross-window: 2024 63%, H1 63%, H2 64%. Variação 2pp em 3 semestres. Candidato mais robusto.

## Comparação cross-window

| Janela | hit | fe | decisão |
|--------|----:|---:|--------|
| 2024-H2 | 63.16% | 10540 | in-sample |
| 2025-H1 (este) | 62.90% | 10376.26 | canary_only |
| 2025-H2 | 64.15% | 10465 | canary (robust) |

**Padrão:** ETH estável 63→63→64 (±2pp) — MAIS ROBUSTO

## Blockers

Nenhum bloqueio técnico.

## Release

release_decision: `canary_only`

## ADR-0019

Stress fee+10 ≡ spread+10 = 10127.76.
