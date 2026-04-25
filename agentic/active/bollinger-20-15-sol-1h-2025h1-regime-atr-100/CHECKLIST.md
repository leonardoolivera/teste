# CHECKLIST.md - AF.3

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only`

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-sol-1h-2025h1-regime-atr-100/`.

## Invariantes

- [x] ADR-0019 (fee+10 ≡ spread+10 = 9427.48).

## Finding

SOL colapsa em 2025 (H1 fe 9770, H2 fe 9264) — ambos perdem capital. Asset instável OOS.
