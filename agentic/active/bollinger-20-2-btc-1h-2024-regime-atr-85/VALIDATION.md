# VALIDATION.md - V.2

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 10005.76.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10218.58 | 1.000 |
| fee+10 | 10118.24 | 0.9902 |
| spread+10 | 10118.24 | 0.9902 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10118.24`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 64.00% | OK |
| 2: mdd <= 35% | 2.22% | OK |
| 3: ratio >= 0.95 | 0.9902 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=85`.
