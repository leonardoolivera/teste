# VALIDATION.md — O.2 RSI 21/35/65 BTC 1h 2024

## Walk-forward (rolling, 5-fold)

4 folds efetivos, 43 trades agregados.

| Fold | final_equity | hit_rate | trades |
| ---- | -----------: | -------: | -----: |
| 1    |      9916.55 |   45.45% |     11 |
| 2    |     10012.29 |   44.44% |      9 |
| 3    |     10025.65 |   70.00% |     10 |
| 4    |      9999.98 |   69.23% |     13 |

3/4 folds cruzam 45%. Fold 2 fica **a 0.56 pp de falhar** (44.44%). Amostra
por fold pequena (9-13 trades) amplifica ruído.

## Monte Carlo (1000 resamples, seed=42)

- p5 = 9595.53
- p50 = 10016.13
- p95 = 10357.39

MC p5 baixo (9595 < 10000) — cauda inferior deficitária, pior que N.2.

## Cost stress

| Cenário   | final_equity |  ratio |
| --------- | -----------: | -----: |
| baseline  |      9959.83 |  1.000 |
| fee+10    |      9728.15 | 0.9767 |
| slip+10   |      9913.45 | 0.9953 |
| spread+10 |      9728.15 | 0.9767 |

**ADR-0019 33ª confirmação:** `fee+10 ≡ spread+10 = 9728.15`.
`spread+10/baseline = 0.9767 ≥ 0.95` → Critério 3 OK.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- Property tests RSI verdes.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade (ADR-0025)

| Critério | Observado | Status |
| -------- | --------: | ------ |
| 1: `hit_rate baseline ≥ 45%` | 58.62% | OK |
| 2: `max_drawdown ≤ 35%` | 3.65% | OK |
| 3: `spread+10 / baseline ≥ 0.95` | 0.9767 | OK |

release_decision: `canary_only`.

## Regime filter

`none`.
