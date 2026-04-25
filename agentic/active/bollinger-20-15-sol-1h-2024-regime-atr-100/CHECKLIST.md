# CHECKLIST.md - AE.2

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only`

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-sol-1h-2024-regime-atr-100/`.

## Invariantes

- [x] ADR-0019 (fee+10 ≡ spread+10 = 10824.71).

## Finding

fe 11210 é MELHOR fe do protocolo (supera R.1 SOL 20/2 fe=10803); 20/1.5 é superior a 20/2 em SOL 2024
