# VALIDATION.md - Y.2

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 8761.82.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 9580.01 | 1.000 |
| fee+10 | 9209.22 | 0.9613 |
| spread+10 | 9209.22 | 0.9613 |

**ADR-0019:** `fee+10 ≡ spread+10 = 9209.22`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 45.16% | OK |
| 2: mdd <= 35% | 6.48% | OK |
| 3: ratio >= 0.95 | 0.9613 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=100`.
