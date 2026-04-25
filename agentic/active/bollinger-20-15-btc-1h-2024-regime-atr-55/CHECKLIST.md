# CHECKLIST.md - AE.1

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only`

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-btc-1h-2024-regime-atr-55/`.

## Invariantes

- [x] ADR-0019 (fee+10 ≡ spread+10 = 10137.88).

## Finding

hit 72.62% excelente; fe 10474 > baseline (AE.3 10178); 20/1.5 + filtro supera baseline BTC 2024
