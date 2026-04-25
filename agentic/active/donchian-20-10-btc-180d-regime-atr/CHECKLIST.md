# CHECKLIST.md — H.4 Donchian+regime ATR

## 5 gates (ADR-0020)

| # | Gate | Artefato | Status |
|---|---|---|---|
| 1 | Pesquisa | [SPEC.md](SPEC.md) | ✓ hipótese falseável sobre "regime de volatilidade", critério de refutação explícito + corroboração, experimento controlado duplo (vs H.1 e vs H.3). |
| 2 | Implementação | [IMPLEMENTATION.md](IMPLEMENTATION.md) | ✓ gap mínimo: ATRRegimeFilter + 2 property + 1 CLI test; pre-autorizada em ADR-0022 §Consequences (novos filtros sem nova ADR). |
| 3 | Validação | [VALIDATION.md](VALIDATION.md) | ✓ `pytest -q` 298 passed / 1 skipped (+3 vs H.3); pipeline `validate` end-to-end; 4 JSONs em `results/validation/donchian-20-10-btc-180d-regime-atr/`; dois `compare` rodados (vs H.1, vs H.3). |
| 4 | Auditoria | [BACKTEST.md](BACKTEST.md) + [AUDIT.md](AUDIT.md) | ✓ comparação transversal tripla H.1/H.3/H.4 em BACKTEST.md; release_decision + 4 blockers + 5 lições + recomendações em AUDIT.md. |
| 5 | Release | `release_decision: fail` | ✓ critério 1 viola (26.39% < 45%); corroboração passa pela primeira vez (trade_count=72). Piloto permanece em `agentic/active/` conforme política ADR-0020. |

## Integridade cruzada

- [x] `run.json.flags.regime_filter == "atr_regime:min_atr_bps=50:window=14"` (canonicalização alfabética ADR-0022).
- [x] `walk_forward.json` com 4 folds efetivos (fold 0 pulado); hit_rates 23-36%, nenhum ≥ 45%.
- [x] `monte_carlo.json` 500 resamples seed=42; p5=9017.20 (maior do protocolo); p95=9804.17 (< 10000).
- [x] `cost_stress.json` baseline + 3 cenários; `fee+10 ≡ spread+10 = 8894.38` bit-a-bit (ADR-0019 6ª confirmação).
- [x] `compare` H.1↔H.4: 2 flags diff (`regime_filter`, `run_id`).
- [x] `compare` H.3↔H.4: 2 flags diff (`regime_filter` — valores diferentes, mesma chave — `run_id`). **Primeiro inter-filtro do protocolo.**
- [x] ADR-0022 referenciada em SPEC §11-bis, IMPLEMENTATION §integração, AUDIT §propriedades estruturais.

## Invariantes do protocolo

- [x] ADR-0003 (sem tuning intra-walk-forward): `min_atr_bps=50` escolhido por inspeção antes do piloto.
- [x] ADR-0010 (monotonicidade): cost_stress não levantou `ValidationError`.
- [x] ADR-0019 (`fee+Δ ≡ spread+Δ`): confirmado 6ª vez; 2ª com filtro ativo; 1ª com ATR-family.
- [x] ADR-0020 (5-gate): 6 artefatos presentes.
- [x] ADR-0022 (regime filter): 2º consumidor real; contrato genérico validado (2 famílias compartilham 100% da integração).
