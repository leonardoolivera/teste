# VALIDATION.md - AA.4

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 9987.25.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10341.56 | 1.000 |
| fee+10 | 10260.96 | 0.9922 |
| spread+10 | 10260.96 | 0.9922 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10260.96`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 65.00% | OK |
| 2: mdd <= 35% | 2.64% | OK |
| 3: ratio >= 0.95 | 0.9922 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=105`.
