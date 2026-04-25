# CHECKLIST.md — R.1 Bollinger SOL 1h 2024 + atr_regime:100

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (39º piloto; **candidato a novo rank 1**).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-sol-1h-2024-regime-atr-100/`.
- [x] Dataset J.1 reusado.

## Invariantes

- [x] ADR-0019 39ª confirmação (`fee+10 ≡ spread+10 = 10542.34`, > 10500).
- [x] ADR-0022 neutrality/lookahead/monotonicity.
- [x] ADR-0026 Bollinger causal.

## Ranking

Esperado rank 1 no N=39 (maior fe operacional e maior MC p5 do protocolo).

## Série R — contexto

R.1 é primeiro dos 2 pilotos da Série R (calibração threshold ATR por
asset). R.2 (threshold 150) pendente para mapear curva. Finding central:
**universalidade de filtro é questão de calibração, não de arquitetura**.
