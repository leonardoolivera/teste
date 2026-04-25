# AUDIT.md - T.2 Bollinger BTC 1h 2024 + atr_regime:70

## Hipótese x evidência

44 trades, hit=68.18%, fe=10272.86, MC p5=10081.02, ratio=0.9828.
near BTC median ATR (70.7) - mid-curve; lower trades but fe preserved.

## Curva BTC+atr_regime

Série T mapeia 3 pontos em BTC. Comparar com P.2 (thr=50) e raw.

## Release

release_decision: `canary_only` (gates ADR-0025: hit 68.18%, mdd 3.58%, ratio 0.9828).

## Blockers

Nenhum bloqueio técnico.

## ADR-0019

Série T confirmação. `fee+10 ≡ spread+10 = 10096.49`.

## Finding

Ponto da curva BTC Série T. Método 3-pontos valida sweet spot ≈ quantile 15-25 do ATR cross-asset.
