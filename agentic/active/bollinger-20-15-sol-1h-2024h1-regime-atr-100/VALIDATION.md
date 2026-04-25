# VALIDATION.md - AG.3

> Gate: **validação**.

## Testes executados

- walk_forward: 4 folds
- monte_carlo: 1000 resamples, seed=42
- cost_stress: fee+10 + spread+10

## Invariantes

- ADR-0019: fee+10 ≡ spread+10 = 9584.44
- ADR-0022/0026 causais.

## Artefatos JSON

`results/validation/bollinger-20-15-sol-1h-2024h1-regime-atr-100/`

## Conformidade

Suíte preservada (366 passed, 1 skipped). Zero código novo.
