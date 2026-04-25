# VALIDATION.md - AH.2

> Gate: **validação**.

## Testes executados

- walk_forward: 4 folds
- monte_carlo: 1000 resamples, seed=42
- cost_stress: fee+10 + spread+10

## Invariantes

- ADR-0019: fee+10 ≡ spread+10 = 9891.17
- ADR-0022/0026 causais.

## Artefatos JSON

`results/validation/bollinger-20-15-btc-1h-2023h2-regime-atr-55/`

## Conformidade

Suíte preservada. Zero código novo.
