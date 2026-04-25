# VALIDATION.md — P.2 Bollinger BTC 1h 2024 + atr_regime

## Walk-forward (rolling, 5-fold)

4 folds efetivos, 54 trades agregados.

| Fold | final_equity | hit_rate | trades |
| ---- | -----------: | -------: | -----: |
| 1    |     10112.79 |   75.00% |     12 |
| 2    |     10203.37 |   84.62% |     13 |
| 3    |     10156.82 |   81.82% |     11 |
| 4    |     10126.93 |   72.22% |     18 |

**4/4 folds ≥ 72.22%** — WF mais robusto de todos os 34 pilotos.

## Monte Carlo (1000 resamples, seed=42)

- p5  = 9971.33
- p50 = 10371.19
- p95 = 10675.94

**MC p5 próximo de 10000** (9971.33) — cauda inferior estreita, risco de
perda contido.

## Cost stress

| Cenário   | final_equity |  ratio |
| --------- | -----------: | -----: |
| baseline  |     10316.93 |  1.000 |
| fee+10    |     10028.59 | 0.9721 |
| spread+10 |     10028.59 | 0.9721 |

**ADR-0019 35ª confirmação:** `fee+10 ≡ spread+10 = 10028.5915` — primeira vez
que o cenário stress termina **acima de 10000** (edge sobrevive stress).
`spread+10/baseline = 0.9721 ≥ 0.95` → Critério 3 OK com folga maior que J.2.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- Property tests ATR regime verdes (ADR-0022).
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade (ADR-0025)

| Critério | Observado | Status |
| -------- | --------: | ------ |
| 1: `hit_rate baseline ≥ 45%` | 73.61% | OK |
| 2: `max_drawdown ≤ 35%` | 3.62% | OK |
| 3: `spread+10 / baseline ≥ 0.95` | 0.9721 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:min_atr_bps=50:window=14` (canonicalizado).
