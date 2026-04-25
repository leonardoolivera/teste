# VALIDATION.md - T.1 Bollinger BTC 1h 2024 + atr_regime:35

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 9914.44.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10266.05 | 1.000 |
| fee+10 | 9949.84 | 0.9692 |
| spread+10 | 9949.84 | 0.9692 |

**ADR-0019:** `fee+10 ≡ spread+10 = 9949.84`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 68.35% | OK |
| 2: mdd <= 35% | 3.62% | OK |
| 3: ratio >= 0.95 | 0.9692 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:min_atr_bps=35:window=14`.
