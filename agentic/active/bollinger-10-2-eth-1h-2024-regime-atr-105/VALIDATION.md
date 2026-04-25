# VALIDATION.md - AA.1

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 10027.03.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10265.68 | 1.000 |
| fee+10 | 10105.31 | 0.9844 |
| spread+10 | 10105.31 | 0.9844 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10105.31`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 62.50% | OK |
| 2: mdd <= 35% | 2.40% | OK |
| 3: ratio >= 0.95 | 0.9844 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=105`.
