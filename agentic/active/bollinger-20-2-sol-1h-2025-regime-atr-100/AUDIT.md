# AUDIT.md - W.1

## Hipótese x evidência

OOS 2025-H2 test of R.1 sweet spot. Evidência: 58 trades, hit=53.45%, fe=9475.95, MC p5=8772.55, ratio=0.9757.


## OOS finding

Este piloto testa sweet spot 2024-H2 em dataset 2025-H2 (out-of-sample). Degradação de hit esperada se edge é window-specific.
## Release

release_decision: `canary_only`.

## Blockers

Nenhum bloqueio técnico.

## ADR-0019

Série W confirmação. `fee+10 ≡ spread+10 = 9245.23`.

## Finding

Ponto Série W em curva cross-asset/cross-window.
