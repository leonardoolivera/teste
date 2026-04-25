# CHECKLIST.md — O.2 RSI 21/35/65 BTC 1h 2024

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (33º piloto; terceiro RSI).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/rsi-21-35-65-btc-1h-2024-baseline/`.
- [x] Dataset 2024-H2 reusado.

## Invariantes

- [x] ADR-0019 33ª confirmação (`fee+10 ≡ spread+10 = 9728.15`).
- [x] ADR-0010 monotonicity.
- [x] ADR-0027 causalidade.

## Ranking

Elegível, mas dominado por N.2 em todas as dimensões materiais. Não candidato
a handoff.

## Série O — consolidação

- 2 pilotos (O.1 fail, O.2 canary_only) confirmam sweet spot paramétrico em
  14/30/70 (N.2). RSI sem ganho via parametrização.
