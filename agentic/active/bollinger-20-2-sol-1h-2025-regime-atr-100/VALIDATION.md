# VALIDATION.md - W.1

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 8772.55.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 9475.95 | 1.000 |
| fee+10 | 9245.23 | 0.9757 |
| spread+10 | 9245.23 | 0.9757 |

**ADR-0019:** `fee+10 ≡ spread+10 = 9245.23`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 53.45% | OK |
| 2: mdd <= 35% | 8.21% | OK |
| 3: ratio >= 0.95 | 0.9757 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=100`.
