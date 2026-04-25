# VALIDATION.md - AC.2

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 8930.31.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 9638.96 | 1.000 |
| fee+10 | 9399.92 | 0.9752 |
| spread+10 | 9399.92 | 0.9752 |

**ADR-0019:** `fee+10 ≡ spread+10 = 9399.92`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 55.00% | OK |
| 2: mdd <= 35% | 7.76% | OK |
| 3: ratio >= 0.95 | 0.9752 | OK |

release_decision: `canary_only`.

## Regime filter

`and(atr_regime:window=14:min_atr_bps=100,sma_slope:window=50:min_slope_bps=10)`.
