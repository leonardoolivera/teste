# AUDIT.md - W.2

## Hipótese x evidência

OOS 2025-H2 test of V.1 sweet spot. Evidência: 42 trades, hit=52.38%, fe=10067.14, MC p5=9715.77, ratio=0.9833.


## OOS finding

Este piloto testa sweet spot 2024-H2 em dataset 2025-H2 (out-of-sample). Degradação de hit esperada se edge é window-specific.
## Release

release_decision: `canary_only`.

## Blockers

Nenhum bloqueio técnico.

## ADR-0019

Série W confirmação. `fee+10 ≡ spread+10 = 9899.18`.

## Finding

Ponto Série W em curva cross-asset/cross-window.
