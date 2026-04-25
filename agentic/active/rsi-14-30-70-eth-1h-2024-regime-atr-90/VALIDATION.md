# VALIDATION.md - AB.2

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 10144.65.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10458.17 | 1.000 |
| fee+10 | 10297.41 | 0.9846 |
| spread+10 | 10297.41 | 0.9846 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10297.41`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 67.50% | OK |
| 2: mdd <= 35% | 2.44% | OK |
| 3: ratio >= 0.95 | 0.9846 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=90`.
