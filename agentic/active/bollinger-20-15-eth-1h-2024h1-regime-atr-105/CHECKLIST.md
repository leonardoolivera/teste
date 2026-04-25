# CHECKLIST.md - AG.1

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only`

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-eth-1h-2024h1-regime-atr-105/`.

## Invariantes

- [x] ADR-0019 (fee+10 ≡ spread+10 = 10491.29).

## Finding

ETH confirma estabilidade em 4 janelas (77/63/63/64% hit). 2024-H1 é o melhor (hit 77.5%). 4/4 preservam edge. CANDIDATO OPERACIONAL FORTE.
