# CHECKLIST.md - AD.3

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (passa gates).

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-eth-1h-2025-baseline/`.

## Invariantes

- [x] ADR-0019 (fee+10 ≡ spread+10 = 9643.32).
- [x] ADR-0022/0026 causal.

## Finding

hit 62.62% > 45%; fe > 10000; ratio 0.9575 > 0.95 (marginal) — controle confirma 1.5 std tem edge em ETH sem filtro
