# CHECKLIST.md — Q.1 Bollinger SOL 1h 2024 + atr_regime

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (37º piloto; replicação P.2 cross-asset).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-sol-1h-2024-regime-atr/`.
- [x] Dataset J.1 reusado.

## Invariantes

- [x] ADR-0019 37ª confirmação (`fee+10 ≡ spread+10 = 10367.65`).
- [x] ADR-0022 neutrality/lookahead/monotonicity.
- [x] ADR-0026 Bollinger causal.

## Ranking

Elegível; esperado rank similar a J.1 (marginalmente melhor). Não muda
handoff primário P.2 BTC.

## Série Q — contexto

Q.1 é primeiro dos 2 pilotos da Série Q (replicação cross-asset do filtro
ATR dominante em P.2). **Filtro quase inativo em SOL 2024-H2** — refuta
hipótese de universalidade cross-asset.
