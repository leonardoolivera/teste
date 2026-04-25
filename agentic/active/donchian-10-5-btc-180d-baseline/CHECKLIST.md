# CHECKLIST.md — H.7 Donchian 10/5 BTC 180d

## Gates (pesquisa → implementação → validação → backtest → auditoria)

ADR-0020 estrito. `release_decision: fail` por dupla violação (critério 1 + critério 3).

## Artefatos

- [x] SPEC.md, IMPLEMENTATION.md, VALIDATION.md, BACKTEST.md, AUDIT.md.
- [x] 4 JSONs em `results/validation/donchian-10-5-btc-180d-baseline/`.

## Invariantes

- [x] ADR-0019 9ª confirmação (`fee+10 ≡ spread+10 = 8766.17`).
- [x] ADR-0010 monotonicity.
