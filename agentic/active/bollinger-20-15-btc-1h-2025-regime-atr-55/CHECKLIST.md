# CHECKLIST.md - AD.1

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: fail` (generalização refutada).

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-btc-1h-2025-regime-atr-55/`.

## Invariantes

- [x] ADR-0019 (fee+10 ≡ spread+10 = 9769.78).
- [x] ADR-0022/0026 causal.

## Finding

hit 44.44% < 45% (critério 1 ADR-0025 violado)
