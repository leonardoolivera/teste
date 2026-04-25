# VALIDATION.md — N.2 RSI 14/30/70 BTC 1h 2024

## Walk-forward (rolling, 5-fold)

4 folds efetivos, 47 trades agregados.

| Fold | final_equity | hit_rate | trades |
| ---- | -----------: | -------: | -----: |
| 1    |      9952.37 |   54.55% |     11 |
| 2    |     10008.46 |   60.00% |     10 |
| 3    |     10079.83 |   90.00% |     10 |
| 4    |     10105.22 |   56.25% |     16 |

4/4 folds cruzam 45%. Fold 3 espetacular: 90% hit em 10 trades.

## Monte Carlo (1000 resamples, seed=42)

- p5 = 9878.93
- p50 = 10217.01
- p95 = 10492.00

**MC p5 marginal (9878.93 < 10000)** — ainda negativo, mas −1.21% vs N.1
(−4.31%).

## Cost stress

| Cenário   | final_equity |  ratio |
| --------- | -----------: | -----: |
| baseline  |     10117.99 |  1.000 |
| fee+10    |      9862.02 | 0.9747 |
| slip+10   |     10066.71 | 0.9949 |
| spread+10 |      9862.02 | 0.9747 |

**ADR-0019 30ª confirmação:** `fee+10 ≡ spread+10 = 9862.02`.
`spread+10/baseline = 0.9747 ≥ 0.95` → Critério 3 OK.

## Regime filter

`none`.

## Testes executados

- `pytest` full: **366 passed, 1 skipped**.
- Property tests RSI verdes.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade (ADR-0025)

| Critério | Observado | Status |
| -------- | --------: | ------ |
| 1: `hit_rate baseline ≥ 45%` | 67.19% | OK |
| 2: `max_drawdown ≤ 35%` | 3.46% | OK |
| 3: `spread+10 / baseline ≥ 0.95` | 0.9747 | OK |

release_decision: `canary_only`.
