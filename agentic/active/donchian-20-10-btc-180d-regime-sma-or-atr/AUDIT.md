# AUDIT.md — H.6 Donchian + Composite(sma OR atr)

release_decision: fail

## release_decision

**`fail`**.

Dupla violação: critério 1 (`hit_rate=26.79% < 45%`) + corroboração (`trade_count=112 < 114`). Piloto refuta hipótese "OR inclusivo recupera edge" — OR é o filtro mais parecido com `none` (H.1 110 trades, 25.45% hit); adicionar OR sobre dois filtros já permissivos gera resultado praticamente equivalente a H.1 com leve deslocamento vertical.

## Blockers

Nenhum blocker operacional. Pipeline 100% limpo. Falha exclusiva de mérito de hipótese.

## Finding transversal

**Semântica AND/OR sobre filtros saturados:**

- AND (H.5): concentra em regimes simultaneamente bons — menos trades (74), hit estável (29.73%), mdd mínimo (8.14%).
- OR (H.6): dilui com regimes marginais — muitos trades (112), hit degradado (26.79%), mdd inflado (10.26%).
- Sem filtro (H.1): baseline (110 trades, 25.45%, 10.49%).

**OR ≈ H.1 em assinatura.** O espaço de ativação de `sma_slope(min=10) ∪ atr_regime(min=50)` cobre ~todo o dataset com threshold tão baixo — tornando OR quase um no-op. Thresholds maiores poderiam mover OR para trade_count < 110, mas ADR-0003 proíbe tuning para escapar a refutação.

## Lições transversais acumuladas H.1-H.6

1. **Família de filtros heurísticos causais atingiu plateau irrecuperável** (25-30% hit sobre 6 pilotos). Nem isolados (H.3, H.4), nem AND (H.5), nem OR (H.6) produzem edge ≥45%.
2. **ADR-0019 confirmada 8ª vez** (`fee+10 ≡ spread+10 = 8683.06`). Invariante estrutural extraordinariamente robusto.
3. **ADR-0023 property 2 (OR-permissivo em trade_count) também falha** sobre BTC Donchian real — OR pode reduzir transações vs cada filtro isolado quando barras ativas-extras formam trades longos contínuos em vez de muitos curtos. Reformulação a signal-emission level (já feita em H.5b) cobre o caso.
4. **Semântica composicional é clara mas não resgata.** AND reduz frequência e aumenta estabilidade; OR aumenta frequência e degrada. Ambos ficam sob o piso de 45%.

## Recomendações

- **Descartar família CompositeFilter como via para cruzar 45% em BTC Donchian 180d.** Nenhum modo binário (and/or) ajuda. HMM continua sendo candidato, mas o sinal estatístico de 6 pilotos sugere que o dataset pode simplesmente não ter edge para esta família de estratégia.
- **Virar para dimensões ortogonais** — próximos pilotos (H.7, H.8, H.9, H.10) exploram *asset* (ETH/SOL), *window* (10/5, 40/20) — isolam dataset e hiperparâmetro da estratégia, mantendo pipeline/custos idênticos.
- **ADR-0023 property 2 precisa da mesma reformulação signal-emission** — dívida menor, endereçada indiretamente pelo test já escrito em H.5b que cobre OR também.

---

## Re-auditoria 2026-04-18 (ADR-0025)

release_decision: fail

**Critério vigente:** híbrido (ADR-0025) — `canary_only` exige `hit_rate ≥ 45%` absoluto; `paper_only` exige top-3 por `composite_score` (ADR-0024) com N ≥ 9.

**Snapshot de ranking (2026-04-18, DEFAULT_WEIGHTS de ADR-0024):**

- Rank: **7/12**
- `composite_score`: **4.82**
- `hit_baseline`: **26.79%** (< piso de 45%)
- `fe_baseline`: **9128.87**
- `flags_digest`: `495e9d26b84db4ea`

**Justificativa:** rank 7/12 por `composite_score`; fora do top-3 → permanece `fail` sob ADR-0025. `hit_rate`=26.79% < 45% também impede `canary_only`.

**Decisão original preservada acima.** Esta seção é append imutável; revogações futuras devem ser **nova seção**, nunca edit.
