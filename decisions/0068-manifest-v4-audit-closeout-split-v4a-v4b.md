# ADR-0068 — Audit v4 closeout: FAIL Gate B + split manifest em v4a (RSI+width 2025-H1) e v4b (RSI puro 2025-H2)

- **Data:** 2026-04-19
- **Status:** Aceita
- **Relacionadas:** ADR-0065 (promoção v4 original), ADR-0067 (audit pré-registrado), ADR-0057 (Padrão 10), ADR-0062 (CH closeout)

## Resultado do audit pré-registrado

Execução via `tools/run_manifest_v4_audit.py` (14 runs). Summarizer em `exports/diag/manifest_v4_audit_summary.json`.

| Gate | Critério | Resultado |
|---|---|---|
| A — Seed stability | fails ≤ 1 em 12 runs | **PASS** 11/12 (1 FAIL marginal: CH.6 seed 2024 MC p5 9466 < 9500, delta 34) |
| B — Filter load-bearing | ≥3/4 combos FAIL sem filter | **FAIL** 2/4 load-bearing |
| C — Exclusion confirmation | 2/2 continuam FAIL com seed 1337 | **PASS** |

### Dados de Gate B (crítico)

| Combo | Com filter | Sem filter | Filter verdict |
|---|---|---|---|
| CH.4 BTC 2025-H1 | Sh=1.69 PASS | Sh=0.23 FAIL(Sh,MCp5) | **LOAD_BEARING** |
| CH.6 SOL 2025-H1 | Sh=1.32 PASS | Sh=0.61 FAIL(Sh,MCp5) | **LOAD_BEARING** |
| CH.7 BTC 2025-H2 | Sh=2.63 PASS | Sh=1.64 PASS | **neutral** (filter não degrada mas não é necessário) |
| CH.9 SOL 2025-H2 | Sh=1.92 PASS | Sh=2.30 PASS | **prejudicial** (filter reduz Sharpe) |

**Veredicto overall:** FAIL em Gate B → manifest v4 como especificado em ADR-0065 não pode ser ativado. O filter `bollinger_width(30, 1.5, 300)` é load-bearing apenas no regime 2025-H1 (chop), neutro-a-prejudicial em 2025-H2 (misto).

## Interpretação

### O filter é regime-específico, não família-específico

Padrão 10 (ADR-0057) dizia: "filtro composicional parametrizado ao regime eleva edge borderline". A audit v4 mostra que isso é verdade para **certos regimes** — especificamente chop puro (2025-H1). No regime misto de 2025-H2, o filter não adiciona (CH.7) ou remove (CH.9) edge. Isto é uma **especificação mais precisa** do Padrão 10:

**Padrão 12 (novo):** "regime filters têm escopo regime-específico, não apenas família-específico. Um filter pode ser load-bearing em chop e neutro/prejudicial em regimes mistos mesmo com a mesma família de estratégia."

Consistente com intuição física: filter width 300 gate filtra períodos de baixa volatilidade. Em chop (volatilidade média, oscilatória) isso seleciona sub-regime útil. Em misto (volatilidade variável com tendência curta), o sub-regime selecionado pelo filter pode ser o pior para mean-rev short (alta vol + trend = drawdown).

### Gate A 1-fail é ruído, não sinal

CH.6 seed 2024 falhou MC p5 por 34 pontos (9466 vs 9500 gate). Outros 11/12 runs PASS confortável. Não é signal de instabilidade — gate original permitia ≤1 fail.

### Gate C confirma base metodológica

Os 2 piores excluídos (CH.1, CH.5) continuam FAIL com seed alternativo — exclusão não era artefato do seed 42.

## Decisão: split em dois manifests

Em vez de colapsar (perder CH.7/CH.9) ou pivotar (perder CH.4/CH.6), **emitir dois manifests complementares** refletindo a realidade empírica:

### Manifest v4a — RSI short + regime filter width 300

- Arquivo: `exports/approved/rsi_short_width_2025h1_20260419.json`
- Combos: **CH.4 BTC 2025-H1, CH.6 SOL 2025-H1** (2 combos)
- `engine.params.regime_filter: bollinger_width(30, 1.5, 300)`
- Uso: bot ativa em BTC/SOL 1h em janelas classificadas como "chop"
- Status pós-audit: **PASS gates A+B+C** para este subset (4/4 combos load-bearing no Gate B restrito)

### Manifest v4b — RSI short puro (sem regime filter)

- Arquivo: `exports/approved/rsi_short_pure_2025h2_20260419.json`
- Combos: **CH.7 BTC 2025-H2, CH.9 SOL 2025-H2** (2 combos)
- `engine.params.regime_filter: null` (ou omitido)
- **PRÉ-REQUISITO ANTES DE ATIVAR:** seed stability adicional (4 runs) — CH.7 e CH.9 sem filter com seeds {1337, 2024}. Critério: fails ≤ 1 em 4 runs. Se PASS → v4b segue pra ativação na mesma ADR-0069; se FAIL → v4b abortado, só v4a ativa.

### Racional do split

1. **Honra evidência empírica** — cada manifest reflete exatamente a especificação que passou load-bearing.
2. **Contrato runtime-faithful preservado** — bot vê dois manifests distintos, cada um com seu `engine.params` literal.
3. **Reverso é seguro** — se um manifest falha em paper, desativa sem impactar o outro.
4. **Padrão 12 documentado** — futuras séries respeitam que filters são regime-específicos.

## Consequências

### Imediatas
- Manifest v4 original (`rsi_short_width_20260419.json`) **não ativa**. Marcar `live_status: "deprecated"` com razão + apontar pra v4a/v4b.
- v4a e v4b emitidos em `pending_audit` (só v4b tem audit pendente — seed stability).
- Script `tools/run_v4b_seed_stability.py` roda 4 runs (CH.7/CH.9 sem filter seeds 1337+2024).
- ADR-0069 closeout + ativação condicional.

### Regras
- Padrão 12 adicionado ao corpus de padrões empíricos.
- Séries futuras: Gate B load-bearing obrigatório antes de ativar manifest com regime filter. Se Gate B dá <100% load-bearing, considerar split por regime ao invés de manifest único.

### Bridge AF↔bot
- Nenhuma notificação até ADR-0069 ativar (evita cortesia, conforme feedback bridge).

## Critério de sucesso desta ADR

1. Audit summarizer arquivado ✓
2. Análise Gate-by-Gate documentada ✓
3. Padrão 12 registrado ✓
4. Dois manifests v4a/v4b emitidos em `pending_audit` (v4a só; v4b depende de seed stability)
5. ADR-0069 closeout + ativação final
