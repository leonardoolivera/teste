# VALIDATION.md — P.1 Bollinger BTC 1h 2024 + sma_slope

## Walk-forward (rolling, 5-fold)

4 folds efetivos, 63 trades agregados.

| Fold | final_equity | hit_rate | trades |
| ---- | -----------: | -------: | -----: |
| 1    |     10062.66 |   71.43% |     14 |
| 2    |     10125.94 |   66.67% |     15 |
| 3    |     10056.29 |   75.00% |     12 |
| 4    |     10088.16 |   72.73% |     22 |

4/4 folds cruzam 45% com folga (66.67% a 75.00%). Folds mais robustos que J.2
(J.2: 64.71%-72.73%).

## Monte Carlo (1000 resamples, seed=42)

- p5  = 10003.03
- p50 = 10335.16
- p95 = 10630.54

**MC p5 > 10000 — edge absoluto mais robusto que J.2 (9921.73).**

## Cost stress

| Cenário   | final_equity |  ratio |
| --------- | -----------: | -----: |
| baseline  |     10184.11 |  1.000 |
| fee+10    |      9840.09 | 0.9662 |
| spread+10 |      9840.09 | 0.9662 |

**ADR-0019 34ª confirmação:** `fee+10 ≡ spread+10 = 9840.0884`.
`spread+10/baseline = 0.9662 ≥ 0.95` → Critério 3 OK.

## Testes executados

- `pytest` full: 366 passed, 1 skipped (inalterado).
- Property tests regime filter verdes (ADR-0022 neutrality/lookahead/monotonicity).
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade (ADR-0025)

| Critério | Observado | Status |
| -------- | --------: | ------ |
| 1: `hit_rate baseline ≥ 45%` | 66.28% | OK |
| 2: `max_drawdown ≤ 35%` | 3.63% | OK |
| 3: `spread+10 / baseline ≥ 0.95` | 0.9662 | OK |

release_decision: `canary_only`.

## Regime filter

`sma_slope:min_slope_bps=10:window=50` (canonicalizado alfabeticamente).
