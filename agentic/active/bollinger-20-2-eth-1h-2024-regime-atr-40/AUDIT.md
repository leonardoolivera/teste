# AUDIT.md - T.4 Bollinger ETH 1h 2024 + atr_regime:40

## Hipótese x evidência

82 trades, hit=71.95%, fe=10031.13, MC p5=9667.34, ratio=0.9673.
below ETH q15 (61.3) - near-baseline activation.

## Curva ETH+atr_regime

Série T mapeia 3 pontos em ETH. Comparar com Q.2 (thr=50) e raw.

## Release

release_decision: `canary_only` (gates ADR-0025: hit 71.95%, mdd 5.93%, ratio 0.9673).

## Blockers

Nenhum bloqueio técnico.

## ADR-0019

Série T confirmação. `fee+10 ≡ spread+10 = 9703.40`.

## Finding

Ponto da curva ETH Série T. Método 3-pontos valida sweet spot ≈ quantile 15-25 do ATR cross-asset.
