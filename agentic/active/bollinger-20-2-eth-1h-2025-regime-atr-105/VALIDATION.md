# VALIDATION.md - W.3

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 9520.61.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10077.63 | 1.000 |
| fee+10 | 9909.65 | 0.9833 |
| spread+10 | 9909.65 | 0.9833 |

**ADR-0019:** `fee+10 ≡ spread+10 = 9909.65`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 57.14% | OK |
| 2: mdd <= 35% | 2.53% | OK |
| 3: ratio >= 0.95 | 0.9833 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=105`.
