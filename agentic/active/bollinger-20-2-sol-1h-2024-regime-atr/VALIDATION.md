# VALIDATION.md — Q.1 Bollinger SOL 1h 2024 + atr_regime

## Walk-forward (rolling, 5-fold)

4 folds efetivos, 72 trades agregados.

| Fold | final_equity | hit_rate | trades |
| ---- | -----------: | -------: | -----: |
| 1    |     10222.05 |   72.22% |     18 |
| 2    |      9963.43 |   47.06% |     17 |
| 3    |     10401.18 |   88.24% |     17 |
| 4    |     10090.67 |   65.00% |     20 |

WF idêntico a J.1 em hits/trades (filtro quase inativo). Fold 2 com hit 47.06%
é o de menor amostra (marginal >45%).

## Monte Carlo (1000 resamples, seed=42)

- p5  = 10064.16
- p50 = 10652.85
- p95 = 11257.29

**MC p5 > 10000** — edge absoluto robusto.

## Cost stress

| Cenário   | final_equity |  ratio |
| --------- | -----------: | -----: |
| baseline  |     10716.73 |  1.000 |
| fee+10    |     10367.65 | 0.9674 |
| spread+10 |     10367.65 | 0.9674 |

**ADR-0019 37ª confirmação:** `fee+10 ≡ spread+10 = 10367.65` (2ª vez que
cenário stress termina > 10000; primeira em SOL).
`spread+10/baseline = 0.9674 ≥ 0.95` → Critério 3 OK.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- Property tests ATR regime verdes.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade (ADR-0025)

| Critério | Observado | Status |
| -------- | --------: | ------ |
| 1: `hit_rate baseline ≥ 45%` | 67.82% | OK |
| 2: `max_drawdown ≤ 35%` | 3.43% | OK |
| 3: `spread+10 / baseline ≥ 0.95` | 0.9674 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:min_atr_bps=50:window=14` (canonicalizado).

## Diagnóstico de atividade do filtro

Filtro suprimiu **apenas 1 sinal de 87** em SOL 2024-H2 (entrada 2024-09-15
11:00 → reentrada 2024-09-15 17:00 após ATR cruzar threshold). Volatilidade
de SOL no semestre mantém ATR > 50 bps quase continuamente. **Filtro é
praticamente inativo neste asset/janela.**
