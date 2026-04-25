# 0083 — Série CP closeout: TrendHTF promove SOL 2025-H1 (v4a-trend) — Gate B revelação + correção parcial ADR-0075

**Status:** Accepted — promoção parcial CP.2 (SOL 2025-H1) para v6 candidato; correção interpretativa ADR-0075
**Date:** 2026-04-20
**Deciders:** Usuário + agente (AF)
**Relates to:** ADR-0082 (pré-registro CP), ADR-0079 (CO closeout — Padrão 17), ADR-0075 (CK closeout — Padrão 15 e interpretação corrigida aqui), ADR-0069 (v4a/v4b ativos)

## Resultado

Framework CP aplicado a runs existentes (nenhum run novo). Matriz completa:

### CP principal (TrendHTF como filter primário, mono-SOL)

| Tag | Janela | Trades | Sharpe | MDD% | MC p5 | cost_r | Verdict |
|---|---|---:|---:|---:|---:|---:|---|
| CP.1 | SOL 2024-H2 | 31 | −1.022 | 9.10 | 8938 | 0.9795 | FAIL (Sh, MCp5) |
| **CP.2** | SOL 2025-H1 | 51 | **+1.958** | 4.75 | 9712 | 0.9705 | **PASS** |
| **CP.3** | SOL 2025-H2 | 55 | **+2.708** | 4.86 | 10144 | 0.9741 | **PASS** |

### Gate B (RSI puro, sem filter) + incumbentes comparativos

| Variante | Trades | Sharpe | MDD% | MC p5 | cost_r | Verdict |
|---|---:|---:|---:|---:|---:|---|
| SOL 2024-H2 RSI puro | n/a | n/a | n/a | n/a | n/a | (não arquivado) |
| **SOL 2025-H1 RSI puro** | 90 | **0.615** | 7.26 | 8946 | 0.9551 | **FAIL (Sh, MCp5)** |
| SOL 2025-H2 RSI puro (= v4b active) | 86 | 2.300 | 5.13 | 9898 | 0.9621 | PASS |
| v4a SOL 2025-H1 width (incumbente) | 94 | 1.319 | 5.74 | 9558 | 0.9555 | PASS |
| CH SOL 2025-H2 width | 80 | 1.918 | 4.57 | 9777 | 0.9620 | PASS |

## Avaliação dos gates pré-registrados

### Gate 1 (≥2/3 PASS): **PASS 2/3**

### Gate 2 (CP Sh ≥ incumbente v4 em cada PASS): **PASS 2/2**

- CP.2 vs v4a width: **1.96 > 1.32** (+0.64) ✅
- CP.3 vs v4b puro: **2.71 > 2.30** (+0.41) ✅

### Gate 3 (trend load-bearing: sem trend cai para FAIL): **PASS 1/2**

- **CP.2 SOL 2025-H1:** RSI puro Sh=0.62 → **FAIL** → trend **É load-bearing** ✅
- CP.3 SOL 2025-H2: RSI puro Sh=2.30 → **PASS** → trend **NÃO load-bearing** ❌ (já tem v4b cobrindo)

### Gate 4 promotion rule: **PROMOÇÃO PARCIAL CP.2**

Gate 1+2 PASS em 2/3; Gate 3 PASS em 1/2. Regra: promove onde **Gate 2+3 ambos PASS**, bloqueia onde Gate 3 FAIL.

- **CP.2 (SOL 2025-H1) → qualifica para v6 promotion** (Gate 1+2+3 todos PASS)
- CP.3 (SOL 2025-H2) → NÃO promove (Gate 3 FAIL — v4b puro já cobre)
- CP.1 (SOL 2024-H2) → FAIL, sem cobertura disponível

## Revelação metodológica: correção interpretativa ADR-0075

**ADR-0075 (CK closeout) declarou TrendHTF como "amplificador não load-bearing" e bloqueou promoção.** Gate B naquele audit testou: CK.2 (RSI + width + trend) vs CH.6 (RSI + width só) — concluiu que remover trend mantém PASS (1.96→1.32, ambos PASS).

**Erro interpretativo:** Gate B testou load-bearing **do trend adicionado ao composto com width**, não load-bearing do **trend isolado**. A pergunta correta era: "TrendHTF sozinho substitui width?" não "TrendHTF além de width cai?".

**Resposta correta descoberta via CP:** em SOL 2025-H1, trend-only (sem width) **é load-bearing** (RSI puro 0.62 FAIL). Trend-only supera width-only (1.96 > 1.32). **Trend-only é manifest alternativo legítimo para SOL 2025-H1.**

Padrão 15 permanece válido (lift sem load-bearing = edge fantasma), mas **definição de "load-bearing" exige especificar a baseline**: load-bearing contra RSI puro (sem nenhum filter) é o padrão mais estrito; load-bearing contra composto alternativo é teste diferente. Ambos teem valor.

### Padrão 19 (novo, metodológico, derivado)

**"Gate B load-bearing tem múltiplas baselines — sempre especificar qual. Filter-in-composition load-bearing (remover uma perna de composto) é diferente de filter-vs-naked (remover todo o filter). Promoção de filter como alternativa a outro filter exige filter-vs-naked PASS (filter isolado é load-bearing contra engine puro), não apenas filter-in-composition."**

Implicação prática:
- CK (ADR-0075) foi testado com baseline errada — trend foi comparado contra width-only, não contra naked. Se tivessem rodado RSI puro + trend vs RSI puro naked desde o começo, CP.2 já teria promovido.
- Futuras séries de filter alternativo pré-registrar **ambos** testes: filter-A vs naked (load-bearing estrito) E filter-A vs filter-B (lift sobre incumbente).

## Decisão

### Promoção condicional CP.2 → manifest v6 candidato

Emitir ADR-0084 de promoção v6 `rsi_short_trendhtf_2025h1_sol_20260420.json`: **1 combo** (SOL 2025-H1, RSI + TrendHTF).

**Critérios para ativação (cumpridos):**
1. Gate 1+2+3 todos PASS ✓
2. Sh > incumbente v4a (+0.64) ✓
3. Load-bearing contra naked ✓
4. Runtime invariants preservados (mesmo engine RSI(14/30/70), fixed_notional) ✓

**Stack pós-v6 (se ativado):**

| Manifest | Família | Filter | Regime | Combos |
|---|---|---|---|---|
| v2 | Bollinger long | width 250 | várias | 4 |
| v3 | Bollinger short | width 300 | 2024-H2 + 2025-H1 | 4 |
| v4a | RSI short | width 300 | 2025-H1 chop | 2 |
| v4b | RSI short | none | 2025-H2 misto | 2 |
| **v6 (candidato)** | **RSI short** | **TrendHTF 4h short_only** | **SOL 2025-H1** | **1** |

**v4a SOL 2025-H1 conflito:** v4a já cobre SOL 2025-H1 com width. Duas opções:
1. **Coexistência** (ambos active): duplica exposição em mesmo regime → **não** (viola Padrão 12 espírito de não-duplicar)
2. **v6 substitui v4a.SOL** (v4a fica só com BTC 2025-H1): recomendado — v6 tem Sh melhor (+0.64), load-bearing confirmado, filter direcional semanticamente alinhado com payoff (Padrão 13).

**Recomendação:** v6 substitui v4a.SOL; v4a fica em v4a' com 1 combo (BTC 2025-H1).

Decisão de ativação **depende de usuário autorizar** — promoção v6 afeta stack (bridge deve postar), diferente de CK/CO/CM que eram signal-only sem promoção.

### Não-promoção CP.3 (SOL 2025-H2)

Gate 3 FAIL: RSI puro SOL 2025-H2 já Sh=2.30 (v4b active cobre). Trend adiciona marginal +0.41 sem load-bearing → Padrão 15 bloqueia. v4b permanece como está.

## Consequências

### Imediatas

- **Pendente usuário:** autorizar promoção v6 (emite ADR-0084 + JSON manifest + substitui v4a.SOL por v6).
- Se autorizado: bridge AF↔bot **posta mudança de stack** (primeira mudança desde v4a/v4b 2026-04-19T17:00Z).
- Se não autorizado ou deferido: CP arquivado com análise completa; v6 fica como candidato documentado em ADR-0084 mas `live_status: candidate` (não active).
- Padrão 19 documentado.

### Pesquisa

- Gate B reformulado para próximas séries: sempre pré-registrar **ambos** baselines (naked e incumbente).
- CK/CO conclusões revisitadas: CK foi load-bearing-contra-composto (FAIL, correto para aquele teste) mas não testou load-bearing-contra-naked (que teria sido PASS e promovido CP.2 muito antes). Não invalida ADR-0075 (escopo dele era composto), apenas contextualiza.

### Próximas séries (pós-CP)

1. **(Opção imediata)** Se v6 aprovado: validar load-bearing trend-only em CP.1 análogo ao 2025-H1 — seria CP-audit em outras janelas cross-periodo BTC/ETH (não só mono-SOL). Hipótese: TrendHTF short_only é load-bearing em regimes chop mesmo fora SOL.
2. **CQ — Composição OR width|trend SOL** (ADR-0081 roadmap) — mais fraca, pode adiar.
3. **Ingest pendente** (CN/CM-completo) — decisão usuário.

Recomendação: aguardar autorização v6, depois abrir série de validação cross-asset TrendHTF (nova geração de hipótese).

## Critério de sucesso desta ADR

1. CP.2 promovida condicionalmente v6 candidato ✓
2. CP.3 não-promovida, justificativa documentada ✓
3. Padrão 19 (Gate B múltiplas baselines) formalizado ✓
4. Correção interpretativa ADR-0075 registrada ✓
5. Pendência usuário explícita ✓
6. STATE.md atualizado (próximo)
