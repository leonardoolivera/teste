# VALIDATION.md - Y.1

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 9265.82.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 9923.42 | 1.000 |
| fee+10 | 9533.95 | 0.9608 |
| spread+10 | 9533.95 | 0.9608 |

**ADR-0019:** `fee+10 ≡ spread+10 = 9533.95`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 43.30% | FAIL |
| 2: mdd <= 35% | 3.33% | OK |
| 3: ratio >= 0.95 | 0.9608 | OK |

release_decision: `fail`.

## Regime filter

`atr_regime:window=14:min_atr_bps=55`.
