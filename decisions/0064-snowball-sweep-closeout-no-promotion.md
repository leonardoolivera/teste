# ADR-0064 — Snowball sweep CG/CH closeout: não promove manifest v3b

- **Data:** 2026-04-19
- **Status:** Aceita
- **Relacionadas:** ADR-0028, ADR-0029 (proibição original), ADR-0030 (runtime-faithful), ADR-0058 (manifest v3 CG), ADR-0062 (CH closeout), ADR-0063 (política sizing dual)

## Contexto

ADR-0063 instituiu política dual: toda série de pesquisa agora roda em fixed_notional e snowball em paralelo. Primeira aplicação da política: re-executar CG (Bollinger short + width 300) e CH (RSI short + width 300) — 18 combos — com `--sizing-mode snowball`.

Gate adicional snowball (ADR-0063): para promoção de manifest v3b, snowball deve satisfazer (a) manifest gate padrão, (b) MDD_snow ≤ 1.5 × MDD_fixed, (c) USD_snow > USD_fixed, (d) mesma quantidade ou mais combos aprovados que fixed.

## Resultado empírico

Tabela completa em `exports/diag/snowball_vs_fixed_summary.json`. Destaques:

### CG (Bollinger short + width 300) — 9 pilotos

| Combo | Fixed pass | Snow pass | USD fixed | USD snow | MDD ok |
|---|---|---|---|---|---|
| CG.3 SOL 2024-H2 | PASS | **FAIL(cost_r=0.9494)** | +132.73 | +135.95 | ok |
| CG.4 BTC 2025-H1 | PASS | PASS | +59.23 | +59.33 | ok |
| CG.5 ETH 2025-H1 | PASS | PASS | +243.12 | +245.63 | ok |
| CG.6 SOL 2025-H1 | PASS | **FAIL(cost_r=0.9458)** | +349.48 | +353.58 | ok |

Snowball promoção candidates: **2/9** (CG.4, CG.5). CG.3 e CG.6 regrediram de PASS → FAIL por queda marginal no cost_r (0.9505 → 0.9494 e 0.9512 → 0.9458).

**Total USD CG (4 combos aprovados fixed):** fixed=$784.56, snow=$794.48, **delta=+$9.93** (+1.26%).

### CH (RSI short + width 300) — 9 pilotos

| Combo | Fixed pass | Snow pass | USD fixed | USD snow | MDD ok |
|---|---|---|---|---|---|
| CH.4 BTC 2025-H1 | PASS | PASS | +81.32 | +81.07 | ok |
| CH.6 SOL 2025-H1 | PASS | PASS | +158.71 | +155.81 | ok |
| CH.7 BTC 2025-H2 | PASS | PASS | +81.18 | +81.18 | ok |
| CH.9 SOL 2025-H2 | PASS | PASS | +190.20 | +194.72 | ok |

Snowball promoção candidates: **2/9** (CH.7, CH.9 — delta positivo). CH.4 e CH.6 com delta USD negativo.

**Total USD CH (4 combos aprovados fixed):** fixed=$511.41, snow=$512.77, **delta=+$1.36** (+0.27%).

### MDD snowball gate

18/18 combos passam `MDD_snow ≤ 1.5 × MDD_fixed`. Diferença MDD máxima observada: +0.28pp (CG.5 ETH 8.33 → 8.53). Gate comportou-se como esperado: snowball com gate de manifest já aplicado (MDD≤20) não explode.

## Decisão

**Não promover manifest v3b/v4b snowball.** Critérios:

1. **Delta USD irrisório:** +$11.29 combinado em 8 combos aprovados ($1.4 por combo médio). Está dentro do ruído estatístico e não justifica o overhead de um segundo manifest v3b com runtime-faithful contract separado.
2. **Regressão em 2 combos CG:** CG.3 e CG.6 caíram de PASS → FAIL por cost_r marginal (~0.001 queda). Snowball não preservou o gate principal em 25% dos combos aprovados — violação direta do critério (d).
3. **CH empatado:** 2/4 combos com delta USD negativo. Snowball não capitaliza sistematicamente em RSI+width 300.
4. **Interpretação física:** ADR-0028/0029 proibiram snowball após empírico ETH mostrar degradação +19% → +0.78% PnL e MDD 17% → 23%. Aqui o cenário é diferente (manifest gate já aplicado, MDD≤20), então snowball não explode, mas também não gera ganho material — trades pequenos (~$1–3 de PnL) em capital $10k não movem capital_corrente o suficiente para compounding meaningful em janelas de 6 meses.

**Conclusão:** para os manifests v3 (CG Bollinger) e v4 (CH RSI pendente) o sizing `fixed_notional_literal` continua sendo a escolha ótima. ADR-0028/0029 contextualizados (não revogados) por ADR-0063; a política dual permanece para séries futuras, mas **zero compromisso de promover snowball** se delta não justificar.

## Consequências

- Manifest v3 (CG) permanece em fixed_notional. `exports/approved/bollinger_short_width_20260419.json` inalterado. `live_status: active`.
- Manifest v4 (CH RSI) planejado — segue em fixed_notional (ADR separada quando escrito).
- Séries futuras (CI, CJ, …) continuam rodando dual conforme ADR-0063, mas gate de promoção snowball endurecido: **delta USD ≥ +5% combinado E zero regressão de combos no fixed→snow**. Abaixo disso, fica documentado aqui e segue fixed.
- Bridge AF↔bot: nenhuma notificação necessária — manifest v3 ativo não muda; snowball não é exposto ao bot.

## Artefatos

- `tools/run_cg_snowball_sweep.py`, `tools/run_ch_snowball_sweep.py` — sweeps (18 runs)
- `tools/summarize_snowball_vs_fixed.py` — comparator
- `exports/diag/snowball_vs_fixed_summary.json` — tabela completa persistida
- `results/validation/{cg,ch}-snow-*-short/` — 18 walk-forward runs arquivados
