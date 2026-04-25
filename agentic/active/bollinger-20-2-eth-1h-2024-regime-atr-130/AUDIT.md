# AUDIT.md - T.6 Bollinger ETH 1h 2024 + atr_regime:130

## Hipótese x evidência

14 trades, hit=85.71%, fe=10299.18, MC p5=9953.93, ratio=0.9945.
above ETH q75 (112.8) - over-filter edge: 14tr, trivial ratio 0.9945.

## Curva ETH+atr_regime

Série T mapeia 3 pontos em ETH. Comparar com Q.2 (thr=50) e raw.

## Release

release_decision: `canary_only` (gates ADR-0025: hit 85.71%, mdd 2.31%, ratio 0.9945).

## Blockers

Nenhum bloqueio técnico. Caveat: amostra pequena (tr<20); mapeia lado over-filter.

## ADR-0019

Série T confirmação. `fee+10 ≡ spread+10 = 10242.64`.

## Finding

Ponto da curva ETH Série T. Método 3-pontos valida sweet spot ≈ quantile 15-25 do ATR cross-asset.
