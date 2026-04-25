# VALIDATION.md - AA.3

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 10160.70.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10540.91 | 1.000 |
| fee+10 | 10387.98 | 0.9855 |
| spread+10 | 10387.98 | 0.9855 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10387.98`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 63.16% | OK |
| 2: mdd <= 35% | 2.83% | OK |
| 3: ratio >= 0.95 | 0.9855 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=105`.
