# VALIDATION.md - AA.2

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 9809.84.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10224.43 | 1.000 |
| fee+10 | 10132.07 | 0.9910 |
| spread+10 | 10132.07 | 0.9910 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10132.07`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 52.17% | OK |
| 2: mdd <= 35% | 3.64% | OK |
| 3: ratio >= 0.95 | 0.9910 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=105`.
