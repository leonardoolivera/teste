# VALIDATION.md — Q.2 Bollinger ETH 1h 2024 + atr_regime

## Walk-forward (rolling, 5-fold)

4 folds efetivos, 63 trades agregados.

| Fold | final_equity | hit_rate | trades |
| ---- | -----------: | -------: | -----: |
| 1    |     10076.84 |   82.35% |     17 |
| 2    |      9888.80 |   53.85% |     13 |
| 3    |     10182.41 |   93.75% |     16 |
| 4    |     10027.49 |   64.71% |     17 |

3/4 folds ≥ 64%; fold 2 com 53.85% (>45%). **Fold 3 hit=93.75%** — 2º maior
single-fold hit do protocolo (atrás apenas de P.2 fold 2 84.62% — errata:
maior é aqui).

## Monte Carlo (1000 resamples, seed=42)

- p5  = 9753.11
- p50 = 10371.53
- p95 = 10909.45

MC p5 < 10000 mas +20 vs J.3.

## Cost stress

| Cenário   | final_equity |  ratio |
| --------- | -----------: | -----: |
| baseline  |     10119.65 |  1.000 |
| fee+10    |      9799.73 | 0.9684 |
| spread+10 |      9799.73 | 0.9684 |

**ADR-0019 38ª confirmação:** `fee+10 ≡ spread+10 = 9799.73`.
`spread+10/baseline = 0.9684 ≥ 0.95` → Critério 3 OK.

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- Property tests ATR regime verdes.
- `scripts/validate_artifacts.py`: exit 0.

## Conformidade (ADR-0025)

| Critério | Observado | Status |
| -------- | --------: | ------ |
| 1: `hit_rate baseline ≥ 45%` | 73.75% | OK |
| 2: `max_drawdown ≤ 35%` | 5.93% | OK |
| 3: `spread+10 / baseline ≥ 0.95` | 0.9684 | OK |

release_decision: `canary_only`.

## Regime filter

`atr_regime:min_atr_bps=50:window=14` (canonicalizado).

## Diagnóstico de atividade do filtro

Filtro suprimiu **5 sinais de 85** em ETH 2024-H2 (5.9%). Volatilidade
de ETH é intermediária entre BTC (muitos períodos de baixa vol) e SOL
(quase sempre alta vol) — filtro aciona algumas vezes com efeito positivo.
