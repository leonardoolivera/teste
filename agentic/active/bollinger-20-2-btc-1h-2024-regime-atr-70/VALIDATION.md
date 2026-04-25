# VALIDATION.md - T.2 Bollinger BTC 1h 2024 + atr_regime:70

## Walk-forward

4 folds efetivos.

## Monte Carlo

p5 = 10081.02.

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10272.86 | 1.000 |
| fee+10 | 10096.49 | 0.9828 |
| spread+10 | 10096.49 | 0.9828 |

**ADR-0019:** `fee+10 ≡ spread+10 = 10096.49`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade ADR-0025

| Critério | Observado | Status |
|---|---:|---|
| 1: hit >= 45% | 68.18% | OK |
| 2: mdd <= 35% | 3.58% | OK |
| 3: ratio >= 0.95 | 0.9828 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:min_atr_bps=70:window=14`.
