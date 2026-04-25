# 0084 — Manifest v6 `rsi_short_trendhtf_2025h1_sol` ativado + v4a refatorado (SOL movido para v6)

**Status:** Accepted — v6 ACTIVE desde 2026-04-20T00:00Z; v4a SOL removido (movido para v6)
**Date:** 2026-04-20
**Deciders:** Usuário (autorização explícita "sim") + agente
**Relates to:** ADR-0083 (CP closeout — promoção condicional), ADR-0082 (pré-registro CP), ADR-0079 (CO — Padrão 17), ADR-0068 (v4 split), ADR-0030 (runtime-faithful), ADR-0031 (schema v3)

## Contexto

ADR-0083 qualificou CP.2 (SOL 2025-H1 TrendHTF short_only) para promoção como manifest v6:
- Sh=1.958 > v4a width 1.319 (+0.639)
- Load-bearing vs naked: RSI puro SOL 2025-H1 Sh=0.615 FAIL (Padrão 19)
- Trade count 51 (entre naked 90 e width 94) — qualidade > quantidade
- Filter direcional alinhado ao payoff (Padrão 13 compliant)

Usuário autorizou ativação explicitamente. Este ADR formaliza mudança de stack.

## Decisão

### 1. Emitir v6 `rsi_short_trendhtf_2025h1_sol_20260420.json` com status `active`

**Arquivo:** `exports/approved/rsi_short_trendhtf_2025h1_sol_20260420.json`
**Estrutura:**
- Engine: RSI(14/30/70) short + `trend_htf:htf=4h:sma_window=50:mode=short_only`
- 1 combo: SOLUSDT 1h, 2025-H1
- Runtime invariants: `entry_fill=market_at_open_next_bar`, `sizing=fixed_notional_literal(2000)`, `stop_loss=disabled`, `signal_arbitration=exit_wins_on_tie`
- Source run: `co-audit-noWidth-sol-20250105_20250704-short` (parte do Gate 4 audit CO, reusado)
- Gate B run: `audit-v4-b-sol-20250105_20250704-nofilter` (RSI puro SOL 2025-H1, Sh=0.615 FAIL)

### 2. Refatorar v4a `rsi_short_width_2025h1_20260419.json`

**Combo removido:** SOL 2025-H1 (source_tag CH.6, Sh=1.319 com width)
**Combo retido:** BTC 2025-H1 (source_tag CH.4, Sh=1.688 com width)

**Justificativa:** v6 SOL supera v4a.SOL em todas dimensões (Sh, semantic alignment com Padrão 13). Manter v4a.SOL ativo duplicaria exposição short SOL 2025-H1 com duas configurações diferentes — violaria espírito Padrão 12 (não acumular variantes sobrepostas).

**v4a pós-mudança:** 1 combo (BTC 2025-H1 width). Complementary_to v4b inalterado. Status `active` mantido.

### 3. Stack consolidado pós-v6

| Manifest | Família | Filter | Regime | Combos | Status |
|---|---|---|---|---|---|
| v2 `bollinger_width_regime_20260418.json` | Bollinger long | width 250 | várias | 4 | active |
| v3 `bollinger_short_width_20260419.json` | Bollinger short | width 300 | 2024-H2 + 2025-H1 | 4 | active |
| **v4a (pós-mudança)** | RSI short | width 300 | BTC 2025-H1 chop | **1** | active |
| v4b `rsi_short_pure_2025h2_20260419.json` | RSI short | none | 2025-H2 misto | 2 | active |
| **v6 `rsi_short_trendhtf_2025h1_sol_20260420.json` (NOVO)** | **RSI short** | **TrendHTF 4h short_only** | **SOL 2025-H1 chop** | **1** | **active** |

**Total combos short-side:** 8 (1 v4a + 2 v4b + 1 v6 + 4 v3) — mesmo total pré-mudança (v4a.SOL saiu, v6.SOL entrou).

### 4. Por que v6 é número separado (não v4c)

v4a/v4b são família "RSI short com/sem width" — mesma hipótese de regime filter com escopo variado. v6 é **hipótese distinta**: filter direcional (TrendHTF) como alternativa semanticamente alinhada (Padrão 13) ao filter de regime (width). Incrementar sub-letra (v4c) esconderia a mudança de família de filter; salto para v6 sinaliza mudança estrutural. v5 reservado para possível futuro cross-asset v4 expansion.

## Runtime invariants (preservados de ADR-0030)

v6 herda os 4 invariantes obrigatórios:
- `entry_fill: market_at_open_next_bar`
- `exit_fill: market_at_open_next_bar`
- `sizing: fixed_notional_literal` (notional_per_trade_quote_ccy=2000)
- `stop_loss: disabled`
- `signal_arbitration: exit_wins_on_tie`

Leverage 2× (fracao=0.1, alavancagem_max=2.0) embutida no notional. `disallow_sizing_modes: [snowball, kelly_like, martingale]`.

## Schema compliance (ADR-0031 + adenda ADR-0066)

Adiciona campo **novo** `supersedes_in_stack` (em v6) e `superseded_partial_by` (em v4a) para documentar substituição parcial. Campos são **opcionais** (schema adenda ADR-0066 relaxou `extra="forbid"` para campos documentais) — não quebram validator existente.

Se schema validator rejeitar: patch adicional em ADR-0066 § anexo (criar sub-ADR separada se necessário). Validação a ser executada neste turno.

## Audit Gate B (ADR-0068 / Padrão 12 + Padrão 19)

v6 supera Padrão 12 Gate B **com Padrão 19 revisto:**
- **Filter-vs-naked:** trend-only Sh=1.958 vs RSI naked Sh=0.615 → **load-bearing confirmado** (naked FAIL)
- **Filter-vs-incumbente (v4a width):** trend Sh=1.958 vs width Sh=1.319 → **+0.639 lift (não redundante)**

Ambos gates passam. v4a.SOL saindo não perde combo válido — v6 cobre com filter superior.

## Consequências

### Imediatas

- v6 JSON salvo em `exports/approved/rsi_short_trendhtf_2025h1_sol_20260420.json` ✓
- v4a atualizado (SOL removido, BTC retido + `superseded_partial_by` metadata) ✓
- Schema validation a executar (próximo)
- Bridge AF↔bot **posta mudança de stack** (primeira mudança desde v4a/v4b 2026-04-19T17Z) — próximo
- STATE.md atualizado — próximo

### BotBinance (downstream)

Bot precisa:
1. Remover combo SOL 2025-H1 de v4a no `config/config.json` whitelist (ou marcar deprecated se bot rodar em múltiplos manifests simultaneamente)
2. Adicionar v6 manifest ao whitelist
3. Re-validar v6 combo localmente com runtime-faithful adapter (±20% trades, ±30% PnL, ±1.5pp MDD tolerância)
4. Paper trade antes de live (política usuário sem pressa para live, MEMORY feedback_no_live_deploy_yet)

Envelope v6 esperado (para bot cross-check):
- SOLUSDT 1h 2025-01-05..2025-07-04: 51 trades, Sh 1.96, MDD 4.75%, PnL 7.75%

### Processo

- **Primeira promoção pós-split v4.** Valida que o ciclo pesquisa→série→audit→promoção funciona (12 séries desde split, CP produziu primeiro upgrade).
- **Padrão 19 provou utilidade imediata:** sem ele, CK (ADR-0075) teria permanecido como "não load-bearing" errôneo, v6 nunca seria descoberto. Aplicar retroativamente a CK não-relevante (CK era composto, não filter-solo).

### Risco monitorado

v6 é **1 combo apenas** — robusteza estatística menor que manifests multi-combo. Se v6 live performance divergir materialmente do OOS (Sh<1.0 em paper por 3+ semanas), revisar:
- v6 em deprecated
- SOL 2025-H1 volta pro v4a (width)
- Investigar se trend-only generaliza cross-asset (série CR futura) antes de nova promoção

## Critério de sucesso desta ADR

1. v6 manifest JSON emitido ✓
2. v4a atualizado com combo SOL removido + metadata supersedes ✓
3. Schema validation PASS (a executar)
4. Bridge AF↔bot posta mudança (a executar)
5. STATE.md atualizado (a executar)
6. Stack consolidado documentado ✓
