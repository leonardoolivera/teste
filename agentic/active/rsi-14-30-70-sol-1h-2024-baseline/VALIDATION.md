# VALIDATION.md — N.1 RSI 14/30/70 SOL 1h 2024

> Gate: **validação**. Walk-forward rolling 5-fold + Monte Carlo 1000 + cost
> stress (fee+10, slip+10, spread+10). Custos H.1 (5/2/0 bps).

## Walk-forward (rolling, train_fraction=0.5, min_test_bars=50)

4 folds efetivos, 47 trades agregados.

| Fold | final_equity | hit_rate | trades |
| ---- | -----------: | -------: | -----: |
| 1    |     10082.87 |   66.67% |     12 |
| 2    |      9949.84 |   58.33% |     12 |
| 3    |      9938.21 |   42.86% |      7 |
| 4    |      9989.26 |   56.25% |     16 |

3/4 folds cruzam 45%. Fold 3 abaixo (42.86%, 7 trades), mas agregado baseline
58.73%.

## Monte Carlo (1000 resamples, seed=42)

- p5 = 9568.51
- p50 = 10023.73
- p95 = 10417.59

MC p5 abaixo de capital (9568 < 10000); cauda inferior deficitária — edge RSI
mais marginal que J.1 Bollinger SOL (p5 = 10046).

## Cost stress (ADR-0014 + ADR-0019)

| Cenário   | final_equity |  ratio |
| --------- | -----------: | -----: |
| baseline  |      9850.00 |  1.000 |
| fee+10    |      9598.55 | 0.9745 |
| slip+10   |      9799.67 | 0.9949 |
| spread+10 |      9598.55 | 0.9745 |

**ADR-0019 29ª confirmação:** `fee+10 ≡ spread+10 = 9598.55` bit-idêntico.
`spread+10/baseline = 0.9745 ≥ 0.95` → Critério 3 OK.

## Regime filter

`none` (baseline puro, paridade com Série J).

## Testes executados

- `pytest` full: **366 passed, 1 skipped** (+29 RSI).
- `test_rsi_mean_reversion.py`: 27 unit verde.
- `test_rsi_causal.py`: 100 Hypothesis examples verde.
- `test_cost_monotonicity_rsi.py`: 30 Hypothesis examples × 3 eixos verde.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade (ADR-0025)

| Critério | Observado | Status |
| -------- | --------: | ------ |
| 1: `hit_rate baseline ≥ 45%` | 58.73% | OK |
| 2: `max_drawdown ≤ 35%` | 6.35% | OK |
| 3: `spread+10 / baseline ≥ 0.95` | 0.9745 | OK |

release_decision: `canary_only` (3/3 critérios cruzados).
