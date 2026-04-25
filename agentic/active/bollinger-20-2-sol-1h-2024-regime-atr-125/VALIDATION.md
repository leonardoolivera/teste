# VALIDATION.md - Z.2

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 10085.90.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10498.38 | 1.000 |
| fee+10 | 10325.56 | 0.9835 |
| spread+10 | 10325.56 | 0.9835 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10325.56`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 65.12% | OK |
| 2: mdd <= 35% | 2.89% | OK |
| 3: ratio >= 0.95 | 0.9835 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=125`.
