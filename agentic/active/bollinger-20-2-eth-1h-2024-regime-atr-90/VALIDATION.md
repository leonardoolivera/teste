# VALIDATION.md - T.5 Bollinger ETH 1h 2024 + atr_regime:90

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 9999.42.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10645.47 | 1.000 |
| fee+10 | 10452.38 | 0.9819 |
| spread+10 | 10452.38 | 0.9819 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10452.38`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 75.00% | OK |
| 2: mdd <= 35% | 4.10% | OK |
| 3: ratio >= 0.95 | 0.9819 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:min_atr_bps=90:window=14`.
