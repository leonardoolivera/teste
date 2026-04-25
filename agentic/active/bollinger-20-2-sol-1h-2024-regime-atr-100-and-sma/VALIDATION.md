# VALIDATION.md - X.3

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 10327.29.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10707.20 | 1.000 |
| fee+10 | 10450.05 | 0.9760 |
| spread+10 | 10450.05 | 0.9760 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10450.05`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 68.75% | OK |
| 2: mdd <= 35% | 3.49% | OK |
| 3: ratio >= 0.95 | 0.9760 | OK |

release_decision: `canary_only`.

## Regime filter

`and(atr_regime:window=14:min_atr_bps=100,sma_slope:window=50:min_slope_bps=10)`.
