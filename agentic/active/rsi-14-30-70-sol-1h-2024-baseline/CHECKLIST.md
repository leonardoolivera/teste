# CHECKLIST.md — N.1 RSI 14/30/70 SOL 1h 2024

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (primeiro da Série N; 29º piloto; primeira
família não-Bollinger a cruzar hard gate no regime 1h 2024-H2).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/rsi-14-30-70-sol-1h-2024-baseline/`.
- [x] Dataset 2024-H2 reusado (`solusdt_1h_20240705_20241231_binance_spot`).
- [x] ADR-0027 escrita (família `rsi` em `strategies/families/rsi/`).

## Invariantes

- [x] ADR-0019 29ª confirmação (`fee+10 ≡ spread+10 = 9598.55`).
- [x] ADR-0010 monotonicity (property test RSI verde).
- [x] ADR-0027 causalidade (property test verde).
- [x] Suite `pytest` full: 366 passed, 1 skipped.

## Ranking

Elegível para composite score (ADR-0024) — release_decision válido para
`eligibility=release_decision == 'canary_only'` filter.
