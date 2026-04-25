# CHECKLIST.md — H.6 Donchian + Composite(sma OR atr)

## Gates (pesquisa → implementação → validação → backtest → auditoria)

Percurso ADR-0020 em ordem estrita. Gate **pesquisa** fechado com hipótese OR multi-dimensional (§SPEC), **implementação** com reuso puro ADR-0022+0023, **validação** com conformance table + invariantes, **backtest** com métricas + compare H.5↔H.6, **auditoria** com `release_decision=fail` por dupla violação.

## 5 gates

- [x] SPEC.md — hipótese OR + critérios.
- [x] IMPLEMENTATION.md — reuso puro, mapeamento, comando.
- [x] VALIDATION.md — suite 305, conformance, invariantes.
- [x] BACKTEST.md — métricas cost_stress/WF/MC + compare H.5↔H.6 + quadro H.1..H.6.
- [x] AUDIT.md — `release_decision: fail`, blockers none, 4 lições transversais.

## JSONs

- [x] run.json — canonical `or(atr_regime:...,sma_slope:...)`.
- [x] walk_forward.json — 4 folds; fold 1 único com fe>10000.
- [x] monte_carlo.json — 500 resamples, seed=42, p50=9363.75.
- [x] cost_stress.json — baseline + 3 scenarios.

## Invariantes

- [x] ADR-0019 8ª confirmação (`fee+10 ≡ spread+10 = 8683.06`).
- [x] ADR-0010 monotonicity ok.
- [x] ADR-0023 canonical `or` + comutatividade ok.
