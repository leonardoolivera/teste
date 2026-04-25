# CHECKLIST.md - AH.1

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only`

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-eth-1h-2023h2-regime-atr-105/`.

## Invariantes

- [x] ADR-0019.

## Finding

2023-H2 ETH tem AMOSTRA INSUFICIENTE (10 trades). Filtro ATR:105 quase totalmente inativo em 2023 (baixa vol). Hit 50% é ruído. NÃO confirma 5/5 janelas — é estatisticamente inconclusivo.
