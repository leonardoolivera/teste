# AUDIT.md - AG.2

> Gate: **auditoria**.

## Hipótese × evidência

BTC 2024-H1 marginal: hit 55.7% OK mas fe < 10000. Cross-window BTC: 55/72/58/44% — 2024-H2 foi outlier positivo, não regra.

## Comparação cross-window (BTC 20/1.5+atr)

| Janela | hit | fe |
|--------|----:|---:|
| 2024-H1 (este) | 55.70% | 9977 |
| 2024-H2 (AE.1) | 72.62% | 10474 |
| 2025-H1 (AF.1) | 58.21% | 10360 |
| 2025-H2 (AD.1) | 44.44% | 9985 |

**Padrão:** BTC inconsistente: 2024-H2 foi outlier (72%); outras 3 janelas 44-58%. Não operar.

## Blockers

Nenhum bloqueio técnico.

## Release

release_decision: `canary_only`

## ADR-0019

Stress fee+10 ≡ spread+10 = 9662.34.
