# VALIDATION.md — R.1 Bollinger SOL 1h 2024 + atr_regime:100

## Walk-forward (rolling, 5-fold)

4 folds efetivos, 50 trades agregados.

| Fold | final_equity | hit_rate | trades |
| ---- | -----------: | -------: | -----: |
| 1    |     10151.68 |   64.29% |     14 |
| 2    |     10079.17 |   66.67% |      9 |
| 3    |     10304.02 |   90.91% |     11 |
| 4    |     10165.56 |   68.75% |     16 |

4/4 folds cruzam 45% com folga. Fold 3 hit=90.91% é um dos maiores
single-fold hits do protocolo. **Fold_min_hit=64.29% > J.1=47.06% e
Q.1=47.06%** — filtro **melhora consistência WF** (não só mean).

## Monte Carlo (1000 resamples, seed=42)

- p5  = 10212.03
- p50 = 10696.04
- p95 = 11141.93

**MC p5 = 10212.03 — maior MC p5 do protocolo (38+ pilotos).**

## Cost stress

| Cenário   | final_equity |  ratio |
| --------- | -----------: | -----: |
| baseline  |     10803.68 |  1.000 |
| fee+10    |     10542.34 | 0.9758 |
| spread+10 |     10542.34 | 0.9758 |

**ADR-0019 39ª confirmação:** `fee+10 ≡ spread+10 = 10542.34` (3ª vez
stress > 10000; primeira > 10500).
`spread+10/baseline = 0.9758 ≥ 0.95` → Critério 3 OK com maior folga
entre assets SOL.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- Property tests ATR regime verdes.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade (ADR-0025)

| Critério | Observado | Status |
| -------- | --------: | ------ |
| 1: `hit_rate baseline ≥ 45%` | 70.77% | OK |
| 2: `max_drawdown ≤ 35%` | 3.43% | OK |
| 3: `spread+10 / baseline ≥ 0.95` | 0.9758 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:min_atr_bps=100:window=14`.
