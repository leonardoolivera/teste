# AUDIT.md - T.5 Bollinger ETH 1h 2024 + atr_regime:90

## Hipótese x evidência

48 trades, hit=75.00%, fe=10645.47, MC p5=9999.42, ratio=0.9819.
near ETH median (88.7) - SWEET SPOT candidate: fe 10645, hit 75%, ratio 0.9819.

## Curva ETH+atr_regime

Série T mapeia 3 pontos em ETH. Comparar com Q.2 (thr=50) e raw.

## Release

release_decision: `canary_only` (gates ADR-0025: hit 75.00%, mdd 4.10%, ratio 0.9819).

## Blockers

Nenhum bloqueio técnico.

## ADR-0019

Série T confirmação. `fee+10 ≡ spread+10 = 10452.38`.

## Finding

Ponto da curva ETH Série T. Método 3-pontos valida sweet spot ≈ quantile 15-25 do ATR cross-asset.
