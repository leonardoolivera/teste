# VALIDATION.md - AC.1

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 9728.18.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10465.68 | 1.000 |
| fee+10 | 10252.97 | 0.9797 |
| spread+10 | 10252.97 | 0.9797 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10252.97`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 64.15% | OK |
| 2: mdd <= 35% | 2.50% | OK |
| 3: ratio >= 0.95 | 0.9797 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:window=14:min_atr_bps=105`.
