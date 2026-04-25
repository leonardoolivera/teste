# CHECKLIST.md — Q.2 Bollinger ETH 1h 2024 + atr_regime

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (38º piloto; replicação P.2 cross-asset).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-eth-1h-2024-regime-atr/`.
- [x] Dataset J.3 reusado.

## Invariantes

- [x] ADR-0019 38ª confirmação (`fee+10 ≡ spread+10 = 9799.73`).
- [x] ADR-0022 neutrality/lookahead/monotonicity.
- [x] ADR-0026 Bollinger causal.

## Ranking

Elegível; esperado subir em relação a J.3 (melhor em todas as métricas).

## Série Q — consolidação

- 2 pilotos (Q.1 SOL inativo, Q.2 ETH domina J.3) revelam que **ganho
  do filtro ATR depende da distribuição de volatilidade do asset**.
  Espectro BTC > ETH > SOL em utilidade. Filtro é universalmente **safe**
  (não piora) mas não universalmente **valioso**. P.2 BTC permanece
  handoff primário.
