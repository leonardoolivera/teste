# VALIDATION.md — R.2 Bollinger SOL 1h 2024 + atr_regime:150

## Walk-forward (rolling, 5-fold)

4 folds efetivos, 16 trades agregados. **Amostra fragmentada por fold**
(3-5 trades cada).

| Fold | final_equity | hit_rate | trades |
| ---- | -----------: | -------: | -----: |
| 1    |     10054.00 |  100.00% |      4 |
| 2    |     10080.52 |   66.67% |      3 |
| 3    |     10167.38 |   75.00% |      4 |
| 4    |      9987.33 |   60.00% |      5 |

Fold 1 hit=100% com 4 trades — **ruído amostral, não signal**. Fold 4 com
5 trades e fe abaixo de 10000. **Amostra pequena demais por fold para
inferência estatística válida.**

## Monte Carlo (1000 resamples, seed=42)

- p5  = 10074.98
- p50 = 10291.71
- p95 = 10557.98

MC p5 > 10000 mas distribuição estreita (p95-p5 = 483, muito menor que
R.1 = 930) por conta de amostra de apenas 26 trades.

## Cost stress

| Cenário   | final_equity |  ratio |
| --------- | -----------: | -----: |
| baseline  |     10420.94 |  1.000 |
| fee+10    |     10316.21 | 0.9899 |
| spread+10 |     10316.21 | 0.9899 |

**ADR-0019 40ª confirmação:** `fee+10 ≡ spread+10 = 10316.21`.
`spread+10/baseline = 0.9899` — **maior ratio do protocolo** (amostra
pequena limita custo acumulado; trivialmente bom).

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade (ADR-0025)

| Critério | Observado | Status |
| -------- | --------: | ------ |
| 1: `hit_rate baseline ≥ 45%` | 65.38% | OK |
| 2: `max_drawdown ≤ 35%` | 2.92% | OK |
| 3: `spread+10 / baseline ≥ 0.95` | 0.9899 | OK |

release_decision: `canary_only` **com caveat**: amostra de 26 trades é
marginal para decisão operacional confiável. Dominado por R.1.

## Regime filter

`atr_regime:min_atr_bps=150:window=14`.
