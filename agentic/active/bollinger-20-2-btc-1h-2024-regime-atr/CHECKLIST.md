# CHECKLIST.md — P.2 Bollinger BTC 1h 2024 + atr_regime

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (35º piloto; **novo candidato primário a
handoff BotBinance — primeiro a dominar J.2 em todas as dimensões**).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-btc-1h-2024-regime-atr/`.
- [x] Dataset J.2 reusado.

## Invariantes

- [x] ADR-0019 35ª confirmação (`fee+10 ≡ spread+10 = 10028.5915` > 10000).
- [x] ADR-0022 neutrality/lookahead/monotonicity.
- [x] ADR-0026 Bollinger causal.

## Ranking

Elegível; esperado rank 1 no leaderboard N=36 (score > J.2=7.64).

## Série P — contexto

P.2 é o **vencedor da Série P**. P.1 (sma_slope) cai abaixo de J.2; P.2
(atr_regime) domina; P.3 (composite AND) pendente para checar se AND é
melhor que ATR puro.
