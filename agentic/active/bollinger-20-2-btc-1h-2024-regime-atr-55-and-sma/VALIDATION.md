# VALIDATION.md - X.1

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 9996.73.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10321.55 | 1.000 |
| fee+10 | 10053.18 | 0.9740 |
| spread+10 | 10053.18 | 0.9740 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10053.18`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 71.64% | OK |
| 2: mdd <= 35% | 3.63% | OK |
| 3: ratio >= 0.95 | 0.9740 | OK |

release_decision: `canary_only`.

## Regime filter

`and(atr_regime:window=14:min_atr_bps=55,sma_slope:window=50:min_slope_bps=10)`.
