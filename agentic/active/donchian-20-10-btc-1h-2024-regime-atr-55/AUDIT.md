# AUDIT.md - Y.1

## Hipótese x evidência

Donchian BTC + atr - cross-strategy filter test. Evidência: 97 trades, hit=43.30%, fe=9923.42, MC p5=9265.82, ratio=0.9608.

## Release

release_decision: `fail`.

## Blockers

Nenhum bloqueio técnico. Gate 1 falhou (hit 43.30% < 45%); release fail.

## ADR-0019

Série Y confirmação. `fee+10 ≡ spread+10 = 9533.95`.

## Finding

Ponto Série Y em curva cross-asset/cross-window.
