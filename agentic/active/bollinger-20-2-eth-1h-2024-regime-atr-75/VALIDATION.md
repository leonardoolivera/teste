# VALIDATION.md - U.1

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 10051.12.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10420.95 | 1.000 |
| fee+10 | 10184.35 | 0.9773 |
| spread+10 | 10184.35 | 0.9773 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10184.35`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 74.58% | OK |
| 2: mdd <= 35% | 4.80% | OK |
| 3: ratio >= 0.95 | 0.9773 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=75`.
