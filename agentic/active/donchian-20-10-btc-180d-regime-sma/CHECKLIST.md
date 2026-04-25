# CHECKLIST.md — H.3 Donchian+regime SMA slope

## 5 gates (ADR-0020)

| # | Gate | Artefato | Status |
|---|---|---|---|
| 1 | Pesquisa | [SPEC.md](SPEC.md) | ✓ hipótese falseável, critério de refutação explícito (3 condições) + corroboração, experimento controlado definido. |
| 2 | Implementação | [IMPLEMENTATION.md](IMPLEMENTATION.md) | ✓ gap zero; SPEC→código mapeado; comando canônico persistido; integração ADR-0022 documentada. |
| 3 | Validação | [VALIDATION.md](VALIDATION.md) | ✓ `pytest -q` 295 passed / 1 skipped; pipeline `validate` end-to-end; 4 JSONs em `results/validation/donchian-20-10-btc-180d-regime-sma/`; `compare` vs H.1 mostra 2 flags diff. |
| 4 | Auditoria | [BACKTEST.md](BACKTEST.md) + [AUDIT.md](AUDIT.md) | ✓ métricas + comparação transversal H.1 em BACKTEST.md; release_decision + 4 blockers + 5 lições + recomendações em AUDIT.md. |
| 5 | Release | `release_decision: fail` | ✓ dupla violação documentada (critério 1 + corroboração); piloto fica em `agentic/active/` até movimentação para `agentic/closed/` por política separada. |

## Integridade cruzada

- [x] `run.json.flags.regime_filter == "sma_slope:min_slope_bps=10:window=50"` (canonicalização alfabética ADR-0022).
- [x] `walk_forward.json` possui `n_folds=4` com fold 2 hit_rate=45.83%.
- [x] `monte_carlo.json` possui 500 resamples seed=42; todos os 5 percentis deslocados para cima vs H.1.
- [x] `cost_stress.json` possui 3 cenários + baseline; `fee+10 ≡ spread+10` bit-a-bit (8741.66).
- [x] `compare` H.1↔H.3 retorna exatamente 2 flags divergentes (`regime_filter`, `run_id`) + 23 iguais.
- [x] ADR-0022 referenciada em SPEC §11-bis, IMPLEMENTATION §integração, AUDIT §propriedades estruturais.

## Invariantes do protocolo

- [x] ADR-0003 (sem tuning intra-walk-forward): `min_slope_bps=10` escolhido por inspeção antes do piloto, não ajustado durante.
- [x] ADR-0010 (monotonicidade): cost_stress não levantou `ValidationError`.
- [x] ADR-0019 (`fee+Δ ≡ spread+Δ`): confirmado (5ª vez; 1ª com filtro ativo).
- [x] ADR-0020 (5-gate): 6 artefatos presentes (SPEC, IMPLEMENTATION, VALIDATION, BACKTEST, AUDIT, CHECKLIST).
- [x] ADR-0022 (regime filter): primeiro consumidor real; canonicalização + causalidade + coerção engine OK.
