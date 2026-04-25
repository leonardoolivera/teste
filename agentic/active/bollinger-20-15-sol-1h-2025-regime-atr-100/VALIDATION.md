# VALIDATION.md - AD.2

> Gate: **validação**.

## Testes executados

- walk_forward: 4 folds (ver `results/validation/bollinger-20-15-sol-1h-2025-regime-atr-100/walk_forward.json`)
- monte_carlo: 1000 resamples, seed=42
- cost_stress: baseline + fee+10 + spread+10

## Invariantes

- ADR-0019: `fee+10 ≡ spread+10 = 8966.53` (bit-identical)
- ADR-0022: filtro ATR causal (quando aplicável)
- ADR-0026: Bollinger SMA-smoothed causal

## Artefatos JSON

`results/validation/bollinger-20-15-sol-1h-2025-regime-atr-100/`: walk_forward.json, monte_carlo.json, cost_stress.json, run.json.

## Conformidade

Todos os testes suíte preservados (366 passed, 1 skipped). Zero código novo.
