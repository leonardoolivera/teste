# VALIDATION.md — S.1 RSI 14/30/70 BTC 1h 2024 + atr_regime:50

## Walk-forward (rolling, 5-fold)

5 folds efetivos, amostra por fold ~10-12 trades.

Folds com hit>60% e fe próximo de 10000 — edge marginal por fold,
consistente com baseline N.2 (sem sinal de degradação por filtro,
mas também sem melhoria).

## Monte Carlo (1000 resamples, seed=42)

- p5  = 9851.08
- p50 = 10186.12
- p95 = 10521.47

p5 < 10000. Distribuição centrada próximo a 10100 — edge marginal.

## Cost stress

| Cenário   | final_equity |  ratio |
| --------- | -----------: | -----: |
| baseline  |     10097.54 |  1.000 |
| fee+10    |      9877.57 | 0.9782 |
| spread+10 |      9877.57 | 0.9782 |

**ADR-0019 41ª confirmação:** `fee+10 ≡ spread+10 = 9877.57`.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade (ADR-0025)

| Critério | Observado | Status |
| -------- | --------: | ------ |
| 1: `hit_rate baseline ≥ 45%` | 65.45% | OK |
| 2: `max_drawdown ≤ 35%` | <35% | OK |
| 3: `spread+10 / baseline ≥ 0.95` | 0.9782 | OK |

release_decision: `canary_only` — passa gates mas **filtro não
agrega valor sobre N.2 raw** em família RSI.

## Regime filter

`atr_regime:min_atr_bps=50:window=14`.
