# VALIDATION.md — O.1 RSI 7/25/75 BTC 1h 2024

## Walk-forward (rolling, 5-fold)

4 folds efetivos, 117 trades agregados.

| Fold | final_equity | hit_rate | trades |
| ---- | -----------: | -------: | -----: |
| 1    |      9884.14 |   57.58% |     33 |
| 2    |     10052.97 |   57.69% |     26 |
| 3    |     10075.28 |   81.48% |     27 |
| 4    |     10214.85 |   64.52% |     31 |

4/4 folds cruzam 45%. Fold 3 = 81.48% (excelente). Consistência superior a N.2
em distribuição por fold.

## Monte Carlo (1000 resamples, seed=42)

- p5 = 9931.16
- p50 = 10297.43
- p95 = 10657.56

MC p5 marginal (9931 < 10000) mas bem acima de todos os pilotos N. Edge médio
superior a RSI 14/30/70.

## Cost stress

| Cenário   | final_equity |  ratio |
| --------- | -----------: | -----: |
| baseline  |     10128.01 |  1.000 |
| fee+10    |      9538.35 | **0.9418** |
| slip+10   |     10009.93 | 0.9883 |
| spread+10 |      9538.35 | **0.9418** |

**ADR-0019 32ª confirmação:** `fee+10 ≡ spread+10 = 9538.35`.
**Critério 3 violado:** `spread+10/baseline = 0.9418 < 0.95`. Custo cumulativo
de 147 trades derruba ratio — mesmo mecanismo da Série L (15m).

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- Property tests RSI verdes.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade (ADR-0025)

| Critério | Observado | Status |
| -------- | --------: | ------ |
| 1: `hit_rate baseline ≥ 45%` | 59.86% | OK |
| 2: `max_drawdown ≤ 35%` | 4.46% | OK |
| 3: `spread+10 / baseline ≥ 0.95` | **0.9418** | **FAIL** |

release_decision: `fail` (1 de 3 critérios violado).

## Regime filter

`none`.
