# VALIDATION.md - Z.1

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 10068.97.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10743.71 | 1.000 |
| fee+10 | 10418.55 | 0.9697 |
| spread+10 | 10418.55 | 0.9697 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10418.55`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 69.14% | OK |
| 2: mdd <= 35% | 3.43% | OK |
| 3: ratio >= 0.95 | 0.9697 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=75`.
