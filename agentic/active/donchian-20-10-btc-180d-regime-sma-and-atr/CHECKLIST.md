# CHECKLIST.md — H.5 Donchian + Composite(sma AND atr)

## Gates atravessados (pesquisa → implementação → validação → backtest → auditoria)

Piloto seguiu ADR-0020 em ordem estrita: **pesquisa** (SPEC) → **implementação** (IMPLEMENTATION: reuso puro ADR-0022+0023) → **validação** (VALIDATION: suite+conformance) → **backtest** (BACKTEST: métricas+compares) → **auditoria** (AUDIT: release_decision=fail). Cada gate produziu artefato dedicado, sem pular etapa.

## 5 gates do ADR-0020

- [x] **SPEC.md** — hipótese + mercado + parâmetros + critério de refutação/corroboração.
- [x] **IMPLEMENTATION.md** — dependências (ADR-0022, ADR-0023), arquivos alterados, reuso puro, comando executado.
- [x] **VALIDATION.md** — suite 303/1, conformance table (critério 1 VIOLA, aux corroboração VIOLA), invariantes estruturais.
- [x] **BACKTEST.md** — métricas cost_stress + WF + MC + compare triplo + quadruple comparison.
- [x] **AUDIT.md** — `release_decision: fail`, finding transversal sobre trade_count, recomendações.

## Artefatos JSON (`results/validation/donchian-20-10-btc-180d-regime-sma-and-atr/`)

- [x] `run.json` — canonical `and(atr_regime:...,sma_slope:...)` persistido.
- [x] `walk_forward.json` — 4 folds efetivos (fold 1: hit 46.67%).
- [x] `monte_carlo.json` — 500 resamples seed 42, p5=9076.24.
- [x] `cost_stress.json` — baseline + 3 scenarios (fee+10, slip+5, spread+10).

## Invariantes protocolares

- [x] **ADR-0019 (7ª confirmação):** `fee+10.fe == spread+10.fe`.
- [x] **ADR-0010 monotonicity:** stress worse-or-equal baseline em fe.
- [x] **ADR-0022 warm-up:** `max(51 SMA, 15 ATR) = 51` barras causais respeitado.
- [x] **ADR-0023 canonical:** filtros internos reordenados lex. (`atr_regime` < `sma_slope`).
- [x] **ADR-0023 comutatividade + roundtrip:** property tests passam.
- [x] **ADR-0002 lookahead:** property test composite confirma.
- [x] **ADR-0003 no tuning intra-walk-forward:** thresholds (slope 10, ATR 50) idênticos a H.3 e H.4 — reuso literal.

## Experimento controlado triplo

- [x] `compare` H.1↔H.5: exatamente 2 flags diff.
- [x] `compare` H.3↔H.5: exatamente 2 flags diff.
- [x] `compare` H.4↔H.5: exatamente 2 flags diff.

## Dívida documentada (para próxima frente)

- [ ] Reescrever ADR-0023 property 1 a nível de signal-emission (trade_count não é estritamente monotônico sob AND — ver H.5 AUDIT.md §Finding transversal chave).
- [ ] Decidir H.6: HMM stateful OR encerramento da série H Donchian/MA BTC 180d.
- [ ] (Opcional) Verificar se H.3 fold 2 e H.5 fold 1 cobrem sub-período sobreposto.
