# AUDIT.md - W.3

## Hipótese x evidência

OOS 2025-H2 test of U.2 sweet spot. Evidência: 42 trades, hit=57.14%, fe=10077.63, MC p5=9520.61, ratio=0.9833.


## OOS finding

Este piloto testa sweet spot 2024-H2 em dataset 2025-H2 (out-of-sample). Degradação de hit esperada se edge é window-specific.
## Release

release_decision: `canary_only`.

## Blockers

Nenhum bloqueio técnico.

## ADR-0019

Série W confirmação. `fee+10 ≡ spread+10 = 9909.65`.

## Finding

Ponto Série W em curva cross-asset/cross-window.
