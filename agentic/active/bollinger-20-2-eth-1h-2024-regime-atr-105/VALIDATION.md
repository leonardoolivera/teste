# VALIDATION.md - U.2

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 10234.37.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10619.72 | 1.000 |
| fee+10 | 10466.63 | 0.9856 |
| spread+10 | 10466.63 | 0.9856 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10466.63`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 73.68% | OK |
| 2: mdd <= 35% | 2.58% | OK |
| 3: ratio >= 0.95 | 0.9856 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=105`.
