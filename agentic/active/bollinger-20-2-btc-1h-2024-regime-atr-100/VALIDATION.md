# VALIDATION.md - T.3 Bollinger BTC 1h 2024 + atr_regime:100

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 10147.85.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10270.78 | 1.000 |
| fee+10 | 10206.30 | 0.9937 |
| spread+10 | 10206.30 | 0.9937 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10206.30`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 75.00% | OK |
| 2: mdd <= 35% | 2.23% | OK |
| 3: ratio >= 0.95 | 0.9937 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:min_atr_bps=100:window=14`.
