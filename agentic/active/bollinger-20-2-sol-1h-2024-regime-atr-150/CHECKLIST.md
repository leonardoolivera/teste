# CHECKLIST.md — R.2 Bollinger SOL 1h 2024 + atr_regime:150

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (40º piloto; **dominado por R.1**,
mapeia lado over-filter da curva).

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-sol-1h-2024-regime-atr-150/`.
- [x] Dataset J.1 reusado.

## Invariantes

- [x] ADR-0019 40ª confirmação (`fee+10 ≡ spread+10 = 10316.21`, maior
  ratio do protocolo = 0.9899 via amostra pequena).
- [x] ADR-0022 neutrality/lookahead/monotonicity.
- [x] ADR-0026 Bollinger causal.

## Ranking

Esperado abaixo de R.1 (fe e hit menores) mas acima de muitos N=38
(ratio 0.9899 puxa score via w_stress=1.0).

## Série R — encerramento

R.1 (threshold 100) = sweet spot, candidato rank 1.
R.2 (threshold 150) = over-filter, dominado.
**Método validado**: mapear 3 pontos de curva antes de deploy.
