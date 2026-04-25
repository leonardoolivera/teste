# CHECKLIST.md — P.1 Bollinger BTC 1h 2024 + sma_slope

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (34º piloto; primeiro regime filter sobre
Bollinger).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-btc-1h-2024-regime-sma/`.
- [x] Dataset J.2 reusado.

## Invariantes

- [x] ADR-0019 34ª confirmação (`fee+10 ≡ spread+10 = 9840.0884`).
- [x] ADR-0022 neutrality/lookahead/monotonicity (property tests).
- [x] ADR-0026 Bollinger causal.

## Ranking

Elegível; cai abaixo de J.2 em hit/fe mas sobe em MC p5. Não candidato a
handoff (J.2 segue primário).

## Série P — contexto

P.1 é primeiro dos 3 pilotos da Série P (regime filter sobre J.2 BTC
Bollinger). P.2 (atr_regime) e P.3 (composite AND) pendentes.
