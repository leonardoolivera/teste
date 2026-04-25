# VALIDATION.md — Donchian 20/10 + Composite(sma AND atr) (H.5)

## Testes executados

- `pytest` completo (unit + integration + property) pós-ADR-0023: **303 passed, 1 skipped**.
- Pipeline `alpha-forge validate` (comando em IMPLEMENTATION.md §Comando executado) gerou 4 artefatos JSON sem erros.
- `alpha-forge compare` H.1↔H.5, H.3↔H.5, H.4↔H.5 — todos com exatamente 2 flags diff.

## Conformidade

## Suite

- Testes unit + integration + property: **303 passed, 1 skipped** pós ADR-0023.
- Tests acrescentados pela frente ADR-0023 (executados antes do piloto):
  - `tests/property/test_composite_filter_canonical.py` — comutatividade + roundtrip.
  - `tests/property/test_composite_filter_lookahead.py` — causalidade herdada.
  - `tests/property/test_composite_filter_restrictive.py` — AND signal-emission ≤ min; OR ≥ max.
  - `tests/integration/test_cli_run_metadata.py::test_regime_filter_composite_and_canonicaliza`.

## Conformance com critério de refutação (SPEC §Critério)

| Critério                                        | Limite       | Observado          | Status      |
| ----------------------------------------------- | ------------ | ------------------ | ----------- |
| 1. `hit_rate` baseline (cost_stress)            | ≥ 45%        | **29.73%**         | **VIOLA**   |
| 2. `max_drawdown` baseline                      | ≤ 35%        | 8.14%              | OK          |
| 3. `final_equity` `spread+10` / baseline        | ≥ 0.95       | 8953.15 / 9247.34 = **0.9682** | OK |

## Conformance com critério de corroboração (SPEC §Critério)

| Condição                                        | Limite       | Observado   | Status         |
| ----------------------------------------------- | ------------ | ----------- | -------------- |
| 3 condições de refutação passam                 | todas        | 1 viola (critério 1) | **N/A — falha antes** |
| `trade_count` baseline `<` H.4 (72)             | estrito      | **74 > 72** | **VIOLA**      |

**Dupla falha:** piloto refutado pelo critério 1 (hit_rate) **e** corroboração falha pelo critério auxiliar de `trade_count`. Ver AUDIT.md para análise da falha de corroboração (finding semântico importante sobre ADR-0023 property 1).

## Invariantes estruturais (cross-validação com ADRs)

| Invariante                                      | Fonte ADR                | Status |
| ----------------------------------------------- | ------------------------ | ------ |
| `fee+10` ≡ `spread+10` em final_equity          | ADR-0019                 | ✅ 8953.15 == 8953.15 (sétima confirmação) |
| `slip+5` monotonic worse than baseline          | ADR-0010                 | ✅ 9217.96 < 9247.34 |
| `spread+10` monotonic worse than baseline       | ADR-0010                 | ✅ 8953.15 < 9247.34 |
| Warm-up = max(filters) + Donchian               | ADR-0022                 | ✅ 51 (SMA bottleneck) |
| Canonical comutativa (atr < sma lex.)           | ADR-0023                 | ✅ `run.json.flags.regime_filter` |
| Canonical roundtrip                             | ADR-0023                 | ✅ property-test |

## Compare triplo (SPEC §Experimento controlado triplo)

Todos os três compares mostram exatamente **2 flags diff** (conforme exigido):

- H.1 ↔ H.5: `regime_filter` (none → and(...)), `run_id`.
- H.3 ↔ H.5: `regime_filter` (sma-only → and(...)), `run_id`.
- H.4 ↔ H.5: `regime_filter` (atr-only → and(...)), `run_id`.

Ver BACKTEST.md §Compare para diffs numéricas completas.

## Walk-forward folds (5-fold rolling)

| fold | fe        | hit_rate  | trades | mdd      |
| ---- | --------- | --------- | ------ | -------- |
| 0    | 9884.54   | 9.09%     | 11     | 1.30%    |
| 1    | 9975.85   | **46.67%**| 15     | 0.66%    |
| 2    | 9687.32   | 25.00%    | 16     | 3.50%    |
| 3    | 9868.60   | 38.46%    | 13     | 3.01%    |

Fold 1 é o segundo fold do protocolo inteiro a cruzar 45% (fold 2 de H.3 foi o primeiro). Evidência adicional de que existe um sub-período do dataset onde filtros causais heurísticos funcionam — mas a exposição fold-agregada continua abaixo do limite.

## Monte Carlo (500 resamples, seed=42)

| percentil | final_equity | max_drawdown |
| --------- | ------------ | ------------ |
| 5         | 9076.24      | 3.30%        |
| 25        | 9257.11      | 5.05%        |
| 50        | 9402.51      | 6.50%        |
| 75        | 9559.40      | 7.70%        |
| 95        | 9808.96      | 9.45%        |

- `p5 = 9076.24` (0.908 × capital) — o maior p5 de qualquer piloto da série Donchian (H.1 p5 ~8700, H.3 p5 ~8920, H.4 p5 ~9000 aprox.).
- `p50 = 9402.51` entre H.3 e H.4, coerente com o fato de AND ser mais restritivo que H.3 mas atingir trade_count próximo de H.4.
