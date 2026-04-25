# CHECKLIST.md - AF.2

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only`

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-eth-1h-2025h1-regime-atr-105/`.

## Invariantes

- [x] ADR-0019 (fee+10 ≡ spread+10 = 10127.76).

## Finding

ETH é MAIS estável cross-window: 2024 63%, H1 63%, H2 64%. Variação 2pp em 3 semestres. Candidato mais robusto.
