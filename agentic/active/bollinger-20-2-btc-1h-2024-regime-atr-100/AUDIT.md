# AUDIT.md - T.3 Bollinger BTC 1h 2024 + atr_regime:100

## Hipótese x evidência

16 trades, hit=75.00%, fe=10270.78, MC p5=10147.85, ratio=0.9937.
above BTC q75 (89.3) - near over-filter edge; 16tr marginal but best ratio/MC p5/hit.

## Curva BTC+atr_regime

Série T mapeia 3 pontos em BTC. Comparar com P.2 (thr=50) e raw.

## Release

release_decision: `canary_only` (gates ADR-0025: hit 75.00%, mdd 2.23%, ratio 0.9937).

## Blockers

Nenhum bloqueio técnico. Caveat: amostra pequena (tr<20); mapeia lado over-filter.

## ADR-0019

Série T confirmação. `fee+10 ≡ spread+10 = 10206.30`.

## Finding

Ponto da curva BTC Série T. Método 3-pontos valida sweet spot ≈ quantile 15-25 do ATR cross-asset.
