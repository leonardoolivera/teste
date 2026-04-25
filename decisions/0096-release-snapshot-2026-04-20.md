# 0096 — Release snapshot 2026-04-20 (fim do ciclo CQ–CX + ingest expansion)

**Status:** Accepted — snapshot
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** todas as ADRs da série desde 2026-04-18 (0030 runtime-faithful onwards)

## Propósito

Fotografia do estado do projeto ao final do dia 2026-04-20. Consolida:
1. Stack approved (todos os manifests ativos)
2. Padrões empíricos formalizados (12–21)
3. Matriz de cobertura (asset × window × direction × engine)
4. Datasets disponíveis
5. Backlog aberto

Futuras sessões devem ler **este snapshot + STATE.md** para contexto rápido antes de qualquer nova série.

## 1. Stack approved (13 combos ativos)

### Pernas long (4 combos)
| Manifest | Version | Symbol | Window | Engine | Sh | Src |
|---|---|---|---|---|---|---|
| bollinger_width_regime_v2 | v2 | ETH | 2024-H1 | Bollinger(20/1.5) long + width(30/1.5/300) | 1.83 | legacy |
| bollinger_width_regime_v2 | v2 | BTC | 2024-H2 | idem | 1.56 | legacy |
| bollinger_width_regime_v2 | v2 | SOL | 2024-H2 | idem | 2.40 | legacy |
| bollinger_width_regime_v2 | v2 | ETH | 2025-H1 | idem | 1.21 | legacy |
| rsi_long_width_eth_2024h2 | v7 | ETH | 2024-H2 | RSI(14/30/70) long + width(30/1.5/300) | 1.77 | CW.2 |

**Correção:** 5 combos long (não 4). v2 bollinger tem 4 combos + v7 tem 1 = 5. Memórias anteriores ("4 long") estavam off-by-one porque ETH 2025-H1 v2 tinha sido contado em outra categoria.

### Pernas short (9 combos)
| Manifest | Version | Symbol | Window | Engine | Sh | Src |
|---|---|---|---|---|---|---|
| bollinger_short_width | v3 | SOL | 2024-H2 | Bollinger(20/1.5) short + width(300) | 1.38 | CG.3 |
| bollinger_short_width | v3 | BTC | 2025-H1 | idem | 1.24 | CG.4 |
| bollinger_short_width | v3 | ETH | 2025-H1 | idem | 2.40 | CG.5 |
| bollinger_short_width | v3 | SOL | 2025-H1 | idem | 2.71 | CG.6 |
| rsi_short_width_2025h1 | v3 (v4a) | BTC | 2025-H1 | RSI short + width(300) | 1.69 | CH.4 |
| rsi_short_pure_2025h2 | v3 (v4b) | BTC | 2025-H2 | RSI short naked | 1.64 | CH.7 |
| rsi_short_pure_2025h2 | v3 (v4b) | SOL | 2025-H2 | RSI short naked | 2.30 | CH.9 |
| rsi_short_trendhtf_2025h1_sol | v6 | SOL | 2025-H1 | RSI short + trend_htf(4h/50/short_only) | 1.96 | CP.2 |

**Total ativo: 13 combos** (5 long + 9 short — contando SOL 2024-H2 short do v3 bollinger que faltou na primeira conta).

**Wait**: re-contando via manifest:
- v2 bollinger long: 4 combos
- v3 bollinger short: 4 combos
- v4a (rsi_short_width_2025h1): 1 combo
- v4b (rsi_short_pure_2025h2): 2 combos
- v6 (rsi_short_trendhtf_sol): 1 combo
- v7 (rsi_long_width_eth_2024h2): 1 combo
- **Total: 13**

v4a-original.json (`rsi_short_width_20260419.json`) está **deprecated** (4 combos inativos — foram refatorados em v4a_2025h1 + v4b).

### Manifests deprecated/superseded
- `bollinger_width_regime_20260418.json` (v1) — superseded por v2
- `rsi_short_width_20260419.json` (v3 original 4-combo) — refatorado em rsi_short_width_2025h1 (1 combo) + rsi_short_pure_2025h2 (2 combos)

**Débito técnico:** v2 bollinger não tem `manifest_version`/`live_status`/`runtime_contract` fields (pré-schema v3). Funciona mas inconsistente. Normalizar em futura sessão.

## 2. Padrões empíricos (12–21)

Ordenados por cronologia de descoberta:

| # | Padrão | Fonte | Status |
|---|---|---|---|
| 12 | Filter load-bearing: Sh(filter) > Sh(naked) + 0.5 para ser promovido | ADR-0036 | Ativo |
| 13 | Filter direção alinhada a payoff (short_only_filter → short_only_side) | ADR-0050 | Ativo |
| 14 | Filter directional é asset-specific (trend_htf funcionou só em SOL) | ADR-0086 | Ativo |
| 15 | Lift sem load-bearing = edge fantasma (Gate B obrigatório) | ADR-0075 | Ativo |
| 16 | Composição (width + trend) redundante em crypto major 1h | ADR-0079 | Ativo |
| 17 | (Mesma ADR-0079, sub-padrão) — idem | ADR-0079 | Ativo |
| 18 | Cross-timeframe 4h inconclusive com 50-bar min (confound) | ADR-0081 | Ativo |
| 19 | Gate B tem múltiplas baselines (filter-vs-naked ≠ filter-vs-incumbente) | ADR-0083 | Ativo |
| 20 | **Crypto major 1h naked: só short-side tem edge** (9+ observações) | ADR-0088/0090 | Regra operacional |
| 21 | **Breakout/trend-following naked é refutável em crypto major 1h** (turnover + whipsaw + double-cost) | ADR-0094 | Regra operacional |

**Padrões 20 e 21 têm força de regra:** pré-registrar nova série naked em crypto major 1h sem filter+directional setup exige justificativa explícita porque o prior é FAIL esperado.

## 3. Matriz de cobertura stack

### Asset × window × direction (engines combinadas)
| Asset | 2024-H1 | 2024-H2 | 2025-H1 | 2025-H2 |
|---|---|---|---|---|
| BTC | — | long (v2) | long-FAIL\*, short×2 (v3+v4a) | short (v4b) |
| ETH | long (v2) | long (v7), short-gap | long (v2), short (v3) | — |
| SOL | — | long (v2), short (v3) | short×2 (v3+v6) | short (v4b) |

\* = testado, não entrou (long-FAIL via Padrão 20)
"gap" = testado mas sem manifest (ex: BTC 2025-H1 long foi CU.1 FAIL; ETH 2025-H2 long foi CV.5 FAIL)

**Observações:**
- 2024-H1: só ETH long testado (janela escassa)
- 2025-H2: só short-side no stack (long naked CV 0/6, filter não testado)
- BTC long: só 2024-H2 (via v2) — filter rescue não aberto para BTC
- DOT/AVAX/LINK: zero combos (dataset novo, CM aberto como próximo)

### Engine × setup
| Engine | Naked | +Width filter | +Trend HTF filter |
|---|---|---|---|
| Bollinger long | n/a | v2 (4) | — |
| Bollinger short | — (CH) | v3 (4) | — |
| RSI long | CU/CV FAIL 0/9 | v7 (1 combo, narrow) | — |
| RSI short | v4b (2) | v4a (1) | v6 (1) |
| Donchian | CX FAIL 0/9 | CY backlog | — |

## 4. Datasets disponíveis (37 total)

Após ingest expansion 2026-04-20 (ADR-0095):

| Symbol | 15m | 1h | 4h |
|---|---|---|---|
| BTCUSDT | 2024-H2 | 2023-H2, 2024-H1, 2024-H2, 2025-H1, 2025-H2 | 2024-H2, 2025-H1, 2025-H2 |
| ETHUSDT | 2024-H2 | 2023-H2, 2024-H1, 2024-H2, 2025-H1, 2025-H2 | 2024-H2, 2025-H1, 2025-H2 |
| SOLUSDT | 2024-H2 | 2023-H2, 2024-H1, 2024-H2, 2025-H1, 2025-H2 | 2024-H2, 2025-H1, 2025-H2 |
| DOTUSDT | — | 2024-H2, 2025-H1, 2025-H2 | — |
| AVAXUSDT | — | 2024-H2, 2025-H1, 2025-H2 | — |
| LINKUSDT | — | 2024-H2, 2025-H1, 2025-H2 | — |
| SYNTHBTC | — | (synthetic) | — |

Todos com sha256 e zero gaps. Bootstrap via `scripts/ingest_binance_vision.py` validado 2026-04-20.

## 5. Backlog aberto

Ordenado por custo ↑ / expected value:

| Série | Hipótese | Runs | Custo | Prob. PASS |
|---|---|---|---|---|
| **CZ** | RSI short naked em DOT/AVAX/LINK 2025-H2 (Padrão 20 cross-universo) | 3 | ~7min | Média — se Padrão 20 vale universal em crypto, PASS esperado |
| CN' | Engines existentes (v2 bollinger long, v3 bollinger short) re-testadas em 4h BTC/ETH/SOL 2025-H1+H2 | 6–12 | ~15-25min | Média — risco gate ≥30 trades |
| CY | Donchian(20,10) + filter rescue (width ou trend_htf) | 9 | ~22min | Baixo-média (Padrão 21 forte) |
| CM' | Bollinger short filter em DOT/AVAX/LINK cross-period | 9 | ~22min | Média — width filter já validado cross-asset BTC/ETH/SOL |
| Normalizar v2 schema | Adicionar manifest_version/live_status/runtime_contract a v2 bollinger | 0 runs | 5min | n/a |

**Nota:** "CM" foi usada em ADR-0080 (cross-timeframe original) e "CN" em backlog interno. Para séries novas após este snapshot, usar **CZ, CZA, CZB, …** para evitar colisão.

## 6. Bridge AF↔bot status

- `inbox_botbinance.md`: último post AF = 2026-04-20T04:50Z (v7 ativação). Signal-only (bot silencia PASS).
- `inbox_alphaforge.md`: último post bot = 2026-04-18T21:00Z. Sem reportes de divergência desde então — assumido PASS implícito para v3, v4a, v4b, v6, v7.
- Paper-mock feed descontinuado (memory saved 2026-04-20). Séries BK/BN/BO encerradas.

## 7. Runtime invariants (ADR-0030)

Ativos em todos os manifests live:
1. `entry_fill`: `market_at_open_next_bar`
2. `exit_fill`: `market_at_open_next_bar`
3. `sizing`: `fixed_notional=2000` USDT (do manifest, não derivado)
4. `stop_loss`: `disabled`
5. `signal_arbitration`: exit wins on tie

`disallow_sizing_modes: [fractional_of_capital, kelly, percent_of_equity]` em manifests v3+.

## 8. Sem pressa para live

Confirmado via memory (`feedback_no_live_deploy_yet`). Todos os manifests v2–v7 estão em **paper-trade** (bot roda em simulação, não toca ordem real). Expansão de pesquisa > canary até usuário dizer o contrário.

## Critério de sucesso desta ADR

1. ✅ Stack inventariado (13 combos active, 2 manifest families deprecated)
2. ✅ Padrões 12–21 listados com status
3. ✅ Matriz de cobertura + gaps explicitados
4. ✅ Datasets consolidados (37 total)
5. ✅ Backlog priorizado
6. ✅ Débito técnico identificado (v2 schema normalization)
7. ⏳ STATE.md aponta para este snapshot como referência rápida
