# 0090 — Série CV closeout: RSI long FAIL 0/6 cross-period → refutação long-side completa + Padrão 20 reforçado

**Status:** Accepted — refutação cross-period total, long-side eliminado
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0089 (pré-registro CV), ADR-0088 (CU closeout + Padrão 20), todos manifests short

## Resultado

| Tag | Asset | Window | Trades | PnL% | MDD% | Sharpe | MC p5 | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---|
| CV.1 | BTC | 2024-H2 | 47 | +1.46 | 1.81 | **+0.886** | 9879 | FAIL (Sh, PnL) |
| CV.2 | ETH | 2024-H2 | 60 | +1.53 | 3.21 | **+0.651** | 9666 | FAIL (Sh, PnL) |
| CV.3 | SOL | 2024-H2 | 47 | −0.40 | 3.40 | **−0.103** | 9569 | FAIL (Sh, PnL) |
| CV.4 | BTC | 2025-H2 | 58 | −4.45 | 5.08 | **−2.343** | 9095 | FAIL (geral) |
| CV.5 | ETH | 2025-H2 | 64 | +1.76 | 4.05 | **+0.669** | 9480 | FAIL (Sh, MCp5, PnL) |
| CV.6 | SOL | 2025-H2 | 60 | +1.17 | 5.60 | **+0.401** | 9099 | FAIL (Sh, MCp5, PnL) |

**PASS = 0/6.**

- **2024-H2 (bull):** 0/3 PASS, avg Sh = +0.48. Melhor BTC Sh=0.89 (próximo gate, insuficiente).
- **2025-H2 (misto):** 0/3 PASS, avg Sh = −0.42. BTC dramaticamente negativo (−2.34).

### Matriz long-side consolidada (CU + CV)

| Asset | 2024-H2 | 2025-H1 | 2025-H2 |
|---|---:|---:|---:|
| BTC | +0.89 | +0.83 | **−2.34** |
| ETH | +0.65 | −0.54 | +0.67 |
| SOL | −0.10 | +0.07 | +0.40 |

**Nenhum combo long PASS em nenhuma janela × asset.** Melhor Sh observado = BTC 2024-H2 = 0.89. Abaixo do gate 1.0.

## Avaliação dos gates pré-registrados

### Gate 1 (≥1/3 por janela): **FAIL 0/6**

### Gate 2 (CV > CU correspondente): parcialmente observado
- BTC 2024-H2 0.89 > CU BTC 2025-H1 0.83 (+0.06, marginal)
- ETH 2024-H2 0.65 > CU ETH 2025-H1 −0.54 (+1.19, hipótese drift-positivo parcialmente apoiada)
- SOL 2024-H2 −0.10 < CU SOL 2025-H1 +0.07 (hipótese refutada para SOL)

Drift-positivo ajuda ETH, neutro BTC, prejudica SOL. Inconclusivo como gate.

### Gate 3 (Promoção v7): **BLOQUEADA 0/6**

### Gate 4 (assimetria): **CONFIRMADA definitivamente**
Long refutado em 3 janelas × 3 assets = 9 casos observados (CU 3 + CV 6). Short-side (v3/v4a/v4b/v6) validado em múltiplos casos no mesmo universo.

## Interpretação

**RSI long(14/30/70) não tem edge em crypto major 1h cross-period** — pelo menos não com engine naked sem filter.

**Possíveis salvações NÃO testadas (deixadas como hipótese):**
1. **Long + regime filter alto-HTF long_only** (análogo ao v6 mas direção oposta). Trend_HTF=long_only filtraria só uptrends macros. Hipótese pode virar série CW futura — risco de overfit a 2024-H2 (única janela bull observada).
2. **Long com thresholds diferentes** (RSI 25/75 em vez de 30/70) — Padrão 16 diz canônico é escopo, mas long pode ter sweet spot diferente. Baixa prioridade.
3. **Long em timeframe diferente** (4h) — bloqueado pelo ingest de janelas 4h (mesmo gargalo CM).

**Decisão pragmática:** não promover CW/CX speculativo agora. Long-side formalmente documentado como "pesquisa exaustiva refutou 2024-H2 + 2025-H1 + 2025-H2 cross-asset naked". Se hipótese nova surgir (e.g., regime filter específico), abrir série dedicada.

## Padrão 20 reforçado (ADR-0088 → ADR-0090)

Texto original Padrão 20: "Refutação cross-asset direcional confirma viés direcional do stack reflete edge real."

**Extensão CV (empírica cross-period):** Padrão 20 agora tem **9 observações** (3 janelas × 3 assets) suportando assimetria direcional em crypto major 1h. Não mais hipótese metodológica — tratamento como **regra operacional**:

> Engine naked em crypto major 1h 2024-H2/2025-H1/2025-H2 só tem edge na direção short. Futuras séries de engine novo (MACD, Stoch, etc.) devem testar primeiro a direção com hipótese priori forte, e rodar direção oposta só como *sanity check* (1 janela 1 ativo, não matriz completa).

Restrição de escopo: **1h crypto major**. Timeframes maiores ou assets diferentes podem ter simetria diferente — não generalizado.

## Stack pós-CU/CV

| Manifest | Família | Direção | Combos |
|---|---|---|---:|
| v2 | Bollinger | long | 4 |
| v3 | Bollinger | short | 4 |
| v4a | RSI width | short | 1 |
| v4b | RSI naked | short | 2 |
| v6 | RSI trend | short | 1 |

**Total:** 4 long (Bollinger v2) + 8 short (restante) = 12 combos. Direcionalmente assimétrico mas cobertura v2 confirma que **long não é impossível** — v2 passou em 2024-H2+2025-H1 com filter width long. Hipótese derivada: **long em crypto 1h exige regime filter**; naked não funciona (CU+CV). v2 pode ser modelo para série CW long+filter.

## Decisão

### Não-promoção CV

v7 não emitido. Stack inalterado. Bridge AF↔bot **não postado** (signal-only).

### Documentar hipótese CW (futura, não aberta agora)

CW = RSI long + regime filter (width OU trend_htf long_only), cross-period cross-asset. Baseada em insight: v2 Bollinger long com width funciona (análogo). Se quiser, abrir depois de meta-análise/paper-check.

## Consequências

### Imediatas
- CV arquivado. v7 não emitido.
- STATE.md atualizado (próximo).
- Bridge não postado.

### Próximas (conforme usuário autorizou plano "1 e 2"):
1. **Meta-análise correlação inter-combos** (8 combos short + 4 v2 long = 12 combos). Objetivo: identificar combos redundantes vs. diversificadores reais. Saída: tabela correlação por janela, sugestão de peso/remoção.
2. **Paper-trade readiness v6/v4b.** Bot confirma que rodou? Envelope observável vs. OOS? Divergência? Tempo desde ativação (v4a/v4b: ~11h, v6: ~4h).

### Padrões cumulativos (snapshot)
1-15: ADRs anteriores
16: threshold canônico = scope
17: composição AND requer FAIL isolado
18: cross-timeframe exige matriz (fraco)
19: Gate B múltiplas baselines
**20 (reforçado):** refutação cross-direcional consolidada — 9 observações long-FAIL confirmam short-only em crypto major 1h, naked. Regra operacional (não só heurística).

## Critério de sucesso desta ADR

1. CV fechado ✓
2. Refutação cross-period documentada ✓
3. Padrão 20 reforçado com evidência empírica ✓
4. Hipótese CW documentada (não aberta) ✓
5. STATE.md atualizado (próximo)
6. Próximos passos meta + paper-check alinhados ✓
