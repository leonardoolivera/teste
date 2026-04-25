# CHECKLIST.md - AD.2

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (passa gates).

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-sol-1h-2025-regime-atr-100/`.

## Invariantes

- [x] ADR-0019 (fee+10 ≡ spread+10 = 8966.53).
- [x] ADR-0022/0026 causal.

## Finding

hit 46.67% > 45% OK; mdd 9% OK; ratio 0.9678 > 0.95 OK — mas fe < 10000 (perde capital)
