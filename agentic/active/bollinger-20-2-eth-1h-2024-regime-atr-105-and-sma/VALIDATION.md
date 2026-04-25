# VALIDATION.md - X.2

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 10111.50.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10564.65 | 1.000 |
| fee+10 | 10415.68 | 0.9859 |
| spread+10 | 10415.68 | 0.9859 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10415.68`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 72.97% | OK |
| 2: mdd <= 35% | 2.59% | OK |
| 3: ratio >= 0.95 | 0.9859 | OK |

release_decision: `canary_only`.

## Regime filter

`and(atr_regime:window=14:min_atr_bps=105,sma_slope:window=50:min_slope_bps=10)`.
