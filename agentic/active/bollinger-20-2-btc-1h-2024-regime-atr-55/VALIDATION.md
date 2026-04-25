# VALIDATION.md - V.1

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 10073.02.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10398.26 | 1.000 |
| fee+10 | 10129.74 | 0.9742 |
| spread+10 | 10129.74 | 0.9742 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10129.74`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 73.13% | OK |
| 2: mdd <= 35% | 3.62% | OK |
| 3: ratio >= 0.95 | 0.9742 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=55`.
