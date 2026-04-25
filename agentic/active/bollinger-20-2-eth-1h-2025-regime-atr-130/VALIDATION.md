# VALIDATION.md - AC.3

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 9547.52.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 9941.28 | 1.000 |
| fee+10 | 9857.49 | 0.9916 |
| spread+10 | 9857.49 | 0.9916 |

**ADR-0019:** `fee+10 ≡ spread+10 = 9857.49`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 61.90% | OK |
| 2: mdd <= 35% | 3.55% | OK |
| 3: ratio >= 0.95 | 0.9916 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=130`.
