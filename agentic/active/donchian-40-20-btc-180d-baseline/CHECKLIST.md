# CHECKLIST.md — H.8 Donchian 40/20 BTC 180d

## Gates (pesquisa → implementação → validação → backtest → auditoria)

Percurso ADR-0020 completo. `release_decision: fail` por critério 1 apenas; critérios 2, 3 e corroboração passam.

## Artefatos

- [x] 6 .md + 4 .json.

## Invariantes

- [x] ADR-0019 10ª confirmação (`fee+10 ≡ spread+10 = 9333.41`).
- [x] ADR-0010 monotonicity.
