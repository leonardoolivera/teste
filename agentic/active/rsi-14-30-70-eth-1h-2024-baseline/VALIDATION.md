# VALIDATION.md — N.3 RSI 14/30/70 ETH 1h 2024

## Walk-forward (rolling, 5-fold)

4 folds efetivos, 60 trades agregados.

| Fold | final_equity | hit_rate | trades |
| ---- | -----------: | -------: | -----: |
| 1    |     10080.55 |   75.00% |     16 |
| 2    |      9881.73 |   50.00% |     12 |
| 3    |     10077.26 |   66.67% |     15 |
| 4    |     10113.90 |   82.35% |     17 |

4/4 folds cruzam 45%. Fold 4 = 82.35% (segundo melhor fold RSI do protocolo).

## Monte Carlo (1000 resamples, seed=42)

- p5 = 9665.78
- p50 = 10128.86
- p95 = 10620.69

**MC p5 < capital (9665.78)** — cauda inferior deficitária, como N.1.

## Cost stress

| Cenário   | final_equity |  ratio |
| --------- | -----------: | -----: |
| baseline  |      9900.11 |  1.000 |
| fee+10    |      9600.61 | 0.9697 |
| slip+10   |      9840.15 | 0.9939 |
| spread+10 |      9600.61 | 0.9697 |

**ADR-0019 31ª confirmação:** `fee+10 ≡ spread+10 = 9600.61`.
`spread+10/baseline = 0.9697 ≥ 0.95` → Critério 3 OK (margem mais apertada do
trio).

## Regime filter

`none`.

## Testes executados

- `pytest` full: **366 passed, 1 skipped**.
- Property tests RSI verdes.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade (ADR-0025)

| Critério | Observado | Status |
| -------- | --------: | ------ |
| 1: `hit_rate baseline ≥ 45%` | 69.33% | OK |
| 2: `max_drawdown ≤ 35%` | 5.71% | OK |
| 3: `spread+10 / baseline ≥ 0.95` | 0.9697 | OK |

release_decision: `canary_only`.
