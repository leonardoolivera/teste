# ADR-0069 — Ativação manifest v4a (RSI+width 2025-H1) e v4b (RSI puro 2025-H2)

- **Data:** 2026-04-19
- **Status:** Aceita — ambos manifests ativam
- **Relacionadas:** ADR-0065 (promoção v4 original), ADR-0067 (audit pré-registrado), ADR-0068 (closeout + split), ADR-0060 (template activate v3)

## Contexto

ADR-0068 dividiu o manifest v4 original em dois: v4a (RSI+width em 2025-H1) e v4b (RSI puro em 2025-H2). V4a saiu do audit v4 com PASS nos 3 gates restritos ao subset. V4b precisava de seed stability extra (CH.7 + CH.9 sem filter em seeds {1337, 2024} = 4 runs) como pré-requisito de ativação.

## Resultado da seed stability v4b

Execução via `tools/run_v4b_seed_stability.py`. Combinado com seed 42 já arquivado em `audit-v4-b-*-nofilter`:

| Combo | Seed 42 | Seed 1337 | Seed 2024 |
|---|---|---|---|
| CH.7 BTC 2025-H2 no-filter | Sh=1.64 MCp5=9796 **PASS** | Sh=1.64 MCp5=9874 **PASS** | Sh=1.64 MCp5=9878 **PASS** |
| CH.9 SOL 2025-H2 no-filter | Sh=2.30 MCp5=9898 **PASS** | Sh=2.30 MCp5=9813 **PASS** | Sh=2.30 MCp5=9817 **PASS** |

**6/6 PASS.** Sharpe/MDD/cost_r bit-stable entre seeds (MC é o único componente seed-dependente; Sharpe é propriedade do walk-forward). Zero fails — gate (fails ≤ 1) folgado.

## Decisão

Ambos manifests transicionam para `live_status: "active"` com timestamp `2026-04-19T17:00:00Z`.

### Manifest v4a — `rsi_short_width_2025h1_20260419.json`

- 2 combos aprovados: CH.4 BTC 2025-H1, CH.6 SOL 2025-H1
- `engine.params.regime_filter: bollinger_width(30, 1.5, 300)` — load-bearing confirmado
- Complementar a v4b e v3 (Bollinger short)

### Manifest v4b — `rsi_short_pure_2025h2_20260419.json`

- 2 combos aprovados: CH.7 BTC 2025-H2, CH.9 SOL 2025-H2
- `engine.params.regime_filter: null` — sem filter é estável-ou-superior
- Complementar a v4a e v3

### Manifest v4 original — `rsi_short_width_20260419.json`

Permanece em `live_status: "deprecated"` com pointer pra v4a+v4b (já aplicado em ADR-0068).

## Complementaridade total (estado pós-ativação)

| Manifest | Família | Filter | Janelas | Combos |
|---|---|---|---|---|
| v1 (legado) | Bollinger long | width 250 | várias | ETHUSDT 2024-H1 (ADR-0028) |
| v2 (legado) | Bollinger long | width 250 | várias | 4 combos (ADR-0029) |
| v3 | Bollinger short | width 300 | 2024-H2 + 2025-H1 | 4 combos (ADR-0058/0060) |
| **v4a** | RSI short | width 300 | 2025-H1 chop | **CH.4 BTC + CH.6 SOL** |
| **v4b** | RSI short | **none** | 2025-H2 misto | **CH.7 BTC + CH.9 SOL** |

Total: **8 combos ativos** em manifests short-side pós-split + 5 legados long-side = 13 combos ativos no stack.

## Consequências

### Imediatas
- `rsi_short_width_2025h1_20260419.json`: `live_status: "active"`, `live_status_since: "2026-04-19T17:00:00Z"`, `audit_closeout_adr: "decisions/0069-...md"`.
- `rsi_short_pure_2025h2_20260419.json`: idem.
- Bridge AF→bot: postar mensagem única consolidada cobrindo ambos manifests + referência à ADR-0068 (split).

### Bot (BotBinance)
- Esperado: re-validar os 4 combos localmente com runtime-faithful adapter. Expect envelope ±20% trades, ±30% PnL, ±1.5pp MDD vs OOS arquivado aqui.
- CH.7 v4b tem 92 trades (sem filter amplia trade count vs 49 com filter); bot deve esperar trade count ~2× maior que v4 original.
- CH.9 v4b tem 86 trades e Sharpe 2.30 (vs 80/1.92 com filter) — ganho real de edge.

### Pesquisa
- Padrão 12 empírico: filter regime-específico. Aplicar em séries futuras — toda série com filter composicional agora exige Gate B load-bearing antes de ativar.
- Próxima série: livre (v4 track fechado). Opções em aberto: Donchian short + width, outros thresholds RSI, cross-timeframe 4h, volume/orderflow filter.

## Critério de sucesso desta ADR

1. Ambos manifests v4a/v4b em `active` ✓
2. Schema validação PASS em ambos ✓
3. ADR-0068 referenciada como audit closeout ✓
4. STATE.md atualizado ✓
5. Bridge AF↔bot notificação enviada ✓
