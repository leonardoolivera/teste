# VALIDATION.md - T.4 Bollinger ETH 1h 2024 + atr_regime:40

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 9667.34.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10031.13 | 1.000 |
| fee+10 | 9703.40 | 0.9673 |
| spread+10 | 9703.40 | 0.9673 |

**ADR-0019:** `fee+10 ≡ spread+10 = 9703.40`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 71.95% | OK |
| 2: mdd <= 35% | 5.93% | OK |
| 3: ratio >= 0.95 | 0.9673 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:min_atr_bps=40:window=14`.
