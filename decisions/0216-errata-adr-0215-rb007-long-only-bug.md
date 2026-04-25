# 0216 — Errata ADR-0215 + reprodutibilidade S08/S10 esclarecida

**Status:** Accepted (errata)
**Date:** 2026-04-25
**Deciders:** Agente, descoberto durante investigação reprodutibilidade ADR-0216 follow-up
**Relates to:** ADR-0215 (Ciclo 2 closeout), [`tools/v2_rb007_stack13_fee_stress.py`](../tools/v2_rb007_stack13_fee_stress.py)

## Contexto

ADR-0215 reportou:
- Stack 13 fee stress: 6/13 ROBUST, 3/13 FEE-FRAGILE, 2/13 NEGATIVO @ baseline (S08, S10).
- Padrão 53 confirmado retroativamente sobre 38% do stack.
- Recomendação follow-up: "ADR-0216: investigação reprodutibilidade S08/S10".

Investigação revelou **bug no script** [`tools/v2_rb007_stack13_fee_stress.py`](../tools/v2_rb007_stack13_fee_stress.py): a CLI default é `--long-only=True` quando nenhum flag é passado. Para combos SHORT do stack 13 (S05, S06, S07, S08, S10, S11, S12, S13 — todos `long_only: false`), o script não passava `--no-long-only`, fazendo a CLI rodar como LONG. Resultado: 8/13 combos rodaram com a estratégia oposta do manifest aprovado.

Audit dos `run.json` flags confirmou:
- S08 ORIG (manifest source_run_id `cg-bol-20-15-sol-...-short`): `long_only: False` ✓
- S08 MINE (rb007 first run): `long_only: True` ✗ — bug.
- S10 ORIG: `long_only: False` ✓
- S10 MINE (first run): `long_only: True` ✗ — bug.

## Fix

Edit em `run_one()`:

```python
# antes (bug):
if combo["long_only"]:
    extra.append("--long-only")

# depois (fixed):
extra.append("--long-only" if combo["long_only"] else "--no-long-only")
```

Re-execução do stack 13 fee stress (39 jobs, 33s wall-clock).

## Resultados corrigidos

| ID | Manifest | Symbol | Window | Sh@5 | Sh@10 | Sh@15 | Tr | Verdict |
|---|---|---|---|---:|---:|---:|---:|---|
| S01 | bollinger_width_regime_v2 | ETH | 2024-H1 | 1.73 | 1.45 | 1.17 | 35 | ROBUST |
| S02 | bollinger_width_regime_v2 | ETH | 2025-H1 | 1.49 | 1.25 | 1.02 | 37 | ROBUST |
| S03 | bollinger_width_regime_v2 | BTC | 2024-H2 | 1.54 | 1.22 | 0.91 | 20 | MARGINAL |
| S04 | bollinger_width_regime_v2 | SOL | 2024-H2 | 2.50 | 2.16 | 1.81 | 55 | ROBUST |
| S05 | bollinger_short_width | SOL | 2024-H2 | 1.38 | 0.96 | 0.54 | 102 | MARGINAL |
| S06 | bollinger_short_width | BTC | 2025-H1 | 1.24 | 0.93 | 0.62 | 37 | MARGINAL |
| S07 | bollinger_short_width | ETH | 2025-H1 | 2.39 | 2.05 | 1.71 | 85 | **ROBUST** |
| S08 | bollinger_short_width | SOL | 2025-H1 | 2.71 | 2.36 | 2.01 | 109 | **ROBUST** |
| S09 | rsi_long_width_eth_2024h2 | ETH | 2024-H2 | 1.77 | 1.43 | 1.08 | 30 | ROBUST |
| S10 | rsi_short_pure_2025h2 | BTC | 2025-H2 | 1.64 | 1.04 | 0.45 | 92 | FEE-FRAGILE |
| S11 | rsi_short_pure_2025h2 | SOL | 2025-H2 | 2.30 | 2.00 | 1.70 | 86 | **ROBUST** |
| S12 | rsi_short_trendhtf_sol_2025h1 | SOL | 2025-H1 | 1.99 | 1.86 | 1.72 | 32 | **ROBUST** |
| S13 | rsi_short_width_2025h1 | BTC | 2025-H1 | 1.69 | 1.38 | 1.07 | 37 | ROBUST |

**Counts corretos:**
- 9/13 ROBUST (S01, S02, S04, S07, S08, S09, S11, S12, S13)
- 3/13 MARGINAL (S03, S05, S06)
- 1/13 FEE-FRAGILE (S10: cai 73% Sh 1.64→0.45 com fees 3x)
- **0/13 NEGATIVO @ baseline** (todos reproduzem manifest stats)

**Reprodutibilidade S08/S10:**
- S08: Sh=2.71 reproduzindo manifest aprovado original Sh=2.713 ✓ (delta < 0.005).
- S10: Sh=1.64 = manifest original Sh=1.64 ✓ (exato).
- **Manifests S08 e S10 estão corretamente reproduzindo. Não há bug de produção.**

## Decisão (errata sobre ADR-0215)

1. **Cancelar conclusão de ADR-0215 sobre "5/13 problemas (38%)"** — leitura inválida por bug do script.
2. **Conclusão correta:** stack 13 é majoritariamente robusto (9/13 ROBUST + 3/13 MARGINAL = 92% sobrevive fee stress 15bps). 1/13 FEE-FRAGILE (S10) merece atenção específica.
3. **Padrão 53 (fees floor) mantém-se válido como princípio**, mas não é "confirmado retroativamente sobre 38% do stack" — apenas 1/13 (8%) é fee-fragile no stack atual. P50 V1 (Padrão 50 candidato) sim era extremo fee-fragile (0/10 com fees 10bps); foi a inspiração do Padrão 53. Stack manifest aprovado é mais resistente que screening V1.
4. **Reprodutibilidade do stack ✓** — manifests aprovados batem com re-execução fresh.
5. **S10 mantém o único caso real** que merece análise dedicada: edge do RSI short BTC 2025-H2 é fee-sensitive — Sh cai 73% de 1.64 a 0.45 com fees 3x. Recomendação: re-validar com fees 10bps default antes de qualquer renewal de approval.

## Lessons (Padrão 55 — script audit before report)

- **Padrão 55:** todo script V2/RAIO que invoca CLI deve passar **explicitamente** todos os boolean flags relevantes (especialmente `--long-only`/`--no-long-only`, `--skip-monte-carlo`, `--skip-cost-stress`). CLI defaults podem mudar entre versões; assumir é frágil.
- Mitigation: adicionar audit script que compara `run.json/payload.flags` esperado vs default antes de declarar resultado.
- Audit retroativo do `tools/v2_rb004_rb007_v1_winners_validation.py`: P50 supertrend não passa `--long-only` flag — possivelmente roda como long-only via CLI default. Mas V1 originais ST01 batch também não passavam. Resultados consistentes mesmo se estratégia bidirectional intended. Não é bug crítico do Cycle 1 (P50 winners eram long-trade-following bear-avoidance — long-only é correto pra esse padrão).

## Consequences

- **Positive:** stack 13 em produção validado (não há manifests negativos), Padrão 53 mantém validade (mas escopo correto), bug script identificado e fixado, Padrão 55 registrado como guarda permanente.
- **Negative:** ADR-0215 §A contém leituras erradas; este errata o supersede em §A. ADR-0215 §B (P52 Sensitivity) e §C (DSR/PSR P52) **não são afetados** — não usavam o script bugado.
- **Neutral:** S10 ainda merece atenção (fee-fragile), mas não é "negativo @ baseline".

## Follow-ups

- Atualizar HYPOTHESIS_TREE, SEARCH_STATE, NODE_LOG, STATE.md, GRAVEYARD com resultado correto.
- Padrão 55 (script audit) → checklist V2/RAIO para todo novo script.
- S10 RSI short BTC 2025-H2: deferir re-validation com fees 10bps default a Ciclo 4 (não-urgente; manifest atual aprovado em 5bps base).

## Não-alvo

- Não revogar ADR-0215 (parts §B e §C válidas); este é erratum focado em §A.
- Não restartar Cycle 1 RB004+RB007 (V1 winners P50/51/52 review não usou bug).
- Não relaxar gate Sh≥1.0 V2 mesmo com correção positiva — disciplina mantida.
