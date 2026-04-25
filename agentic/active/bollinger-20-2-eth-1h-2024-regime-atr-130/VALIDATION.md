# VALIDATION.md - T.6 Bollinger ETH 1h 2024 + atr_regime:130

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 9953.93.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10299.18 | 1.000 |
| fee+10 | 10242.64 | 0.9945 |
| spread+10 | 10242.64 | 0.9945 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10242.64`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 85.71% | OK |
| 2: mdd <= 35% | 2.31% | OK |
| 3: ratio >= 0.95 | 0.9945 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:min_atr_bps=130:window=14`.
