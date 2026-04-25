# VALIDATION.md — P.3 Bollinger BTC 1h 2024 + composite AND

## Walk-forward (rolling, 5-fold)

4 folds efetivos, 50 trades agregados.

| Fold | final_equity | hit_rate | trades |
| ---- | -----------: | -------: | -----: |
| 1    |     10112.79 |   75.00% |     12 |
| 2    |     10153.10 |   81.82% |     11 |
| 3    |     10114.13 |   77.78% |      9 |
| 4    |     10127.19 |   72.22% |     18 |

4/4 folds ≥ 72.22%. Fold 3 com apenas 9 trades (menor amostra do trio P).

## Monte Carlo (1000 resamples, seed=42)

- p5  = 9995.84
- p50 = 10303.78
- p95 = 10577.37

**MC p5 = 9995.84 — melhor do protocolo** (supera P.2=9971.33 e J.2=9921.73).

## Cost stress

| Cenário   | final_equity |  ratio |
| --------- | -----------: | -----: |
| baseline  |     10252.71 |  1.000 |
| fee+10    |      9960.50 | 0.9715 |
| spread+10 |      9960.50 | 0.9715 |

**ADR-0019 36ª confirmação:** `fee+10 ≡ spread+10 = 9960.4985` (primeira sob
`CompositeFilter(mode="and")` — equivalência cross-tipo-de-filtro).
`spread+10/baseline = 0.9715 ≥ 0.95` → Critério 3 OK.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- Property tests CompositeFilter verdes (ADR-0023).
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade (ADR-0025)

| Critério | Observado | Status |
| -------- | --------: | ------ |
| 1: `hit_rate baseline ≥ 45%` | 71.23% | OK |
| 2: `max_drawdown ≤ 35%` | 3.63% | OK |
| 3: `spread+10 / baseline ≥ 0.95` | 0.9715 | OK |

release_decision: `canary_only`.

## Regime filter

`and(atr_regime:min_atr_bps=50:window=14,sma_slope:min_slope_bps=10:window=50)`
(canonicalizado alfabeticamente dentro e entre operandos).
