# VALIDATION.md - AB.1

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 9610.71.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 9913.25 | 1.000 |
| fee+10 | 9705.63 | 0.9791 |
| spread+10 | 9705.63 | 0.9791 |

**ADR-0019:** `fee+10 ≡ spread+10 = 9705.63`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 55.77% | OK |
| 2: mdd <= 35% | 6.35% | OK |
| 3: ratio >= 0.95 | 0.9791 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=100`.
