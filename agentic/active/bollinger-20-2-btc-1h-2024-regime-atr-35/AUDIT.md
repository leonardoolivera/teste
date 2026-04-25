# AUDIT.md - T.1 Bollinger BTC 1h 2024 + atr_regime:35

## Hipótese x evidência

79 trades, hit=68.35%, fe=10266.05, MC p5=9914.44, ratio=0.9692.
below q15 BTC ATR (46.5) - filter mostly inactive, few extra signals.

## Curva BTC+atr_regime

Série T mapeia 3 pontos em BTC. Comparar com P.2 (thr=50) e raw.

## Release

release_decision: `canary_only` (gates ADR-0025: hit 68.35%, mdd 3.62%, ratio 0.9692).

## Blockers

Nenhum bloqueio técnico.

## ADR-0019

Série T confirmação. `fee+10 ≡ spread+10 = 9949.84`.

## Finding

Ponto da curva BTC Série T. Método 3-pontos valida sweet spot ≈ quantile 15-25 do ATR cross-asset.
