# CHECKLIST.md — P.3 Bollinger BTC 1h 2024 + composite AND

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (36º piloto; primeira aplicação de
`CompositeFilter(mode="and")` em Bollinger mean-reversion).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-btc-1h-2024-regime-sma-and-atr/`.
- [x] Dataset J.2 reusado.

## Invariantes

- [x] ADR-0019 36ª confirmação (`fee+10 ≡ spread+10 = 9960.4985`).
- [x] ADR-0022 neutrality/lookahead/monotonicity.
- [x] ADR-0023 CompositeFilter signal-emission property.
- [x] ADR-0026 Bollinger causal.

## Ranking

Elegível; esperado rank entre P.2 e J.2 no leaderboard N=36.

## Série P — consolidação

- 3 pilotos (P.1 sma, P.2 atr, P.3 and) validam **atr_regime é o filtro
  dominante para Bollinger mean-reversion BTC 2024-H2**. P.2 é novo
  candidato primário a handoff; P.1 perde hit/fe marginal; P.3 replica
  finding Série H.5 (AND não supera família pura quando uma já é eficaz).
