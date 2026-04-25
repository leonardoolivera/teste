# CHECKLIST.md — O.1 RSI 7/25/75 BTC 1h 2024

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: fail` (32º piloto; segundo `fail` operacional por
ADR-0025 Critério 3; primeiro por parametrização).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/rsi-7-25-75-btc-1h-2024-baseline/`.
- [x] Dataset 2024-H2 reusado.

## Invariantes

- [x] ADR-0019 32ª confirmação (`fee+10 ≡ spread+10 = 9538.35`).
- [x] ADR-0010 monotonicity.
- [x] ADR-0027 causalidade.

## Ranking

Elegível para ranking mas com `release_decision=fail` — score apenas
informativo; não considerado para handoff.
