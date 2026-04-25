# 0107 — Auditoria Padrão 25: combos do stack ativo promovidos com janela única

**Status:** Accepted — auditoria, plano de triagem
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0106 (CZD + Padrão 25), ADR-0068 (v4 audit), ADR-0083 (v6), ADR-0089 (v7)

## Motivação

Padrão 25 (ADR-0106): promoção ao stack ativo exige ≥2 janelas OOS PASS. LINK entrou em v8 com 1 janela (CZ.3 2025-H2) e CZD expôs window-specific FAIL (Sh flip +1.76→-1.34). Auditar stack pós-rollback (13 combos) para identificar combos com o mesmo risco.

## Inventário (13 combos pós-v8.1)

### Validação cross-window presente (não requer rescue)

| Combo | Janelas validadas | Nota |
|---|---|---|
| BTCUSDT 2025-H2 RSI short (v8.1) | Audit v4 Gate B (CH.7) + v4b seed stability | Cross-window indireto via v4 e audit histórico |
| SOLUSDT 2025-H2 RSI short (v8.1) | Audit v4 Gate B (CH.9) + v4b seed stability | Idem |

### ⚠️ Combos de janela única — candidatos a teste Padrão 25

| Combo | Manifest | Janela única | Sh | Risco |
|---|---|---|---|---|
| **BTC 2025-H1 RSI+width** | v4a | 2025-H1 | 1.688 | Alto — incumbente desde audit v4 |
| **SOL 2025-H1 RSI+trend_htf** | v6 | 2025-H1 | 1.958 | Alto — promovido após CP.2 apenas |
| **ETH 2024-H2 RSI+width long** | v7 | 2024-H2 | 1.774 | **Crítico** — único long, envelope marginal (30 trades = gate floor) |
| **SOL 2024-H2 Bollinger short+width** | v3 | 2024-H2 | 1.380 | Médio — SOL tem 2 janelas distintas em v3 (ver abaixo) |
| **BTC 2025-H1 Bollinger short+width** | v3 | 2025-H1 | 1.243 | Alto |
| **ETH 2025-H1 Bollinger short+width** | v3 | 2025-H1 | 2.395 | Alto |
| **SOL 2025-H1 Bollinger short+width** | v3 | 2025-H1 | 2.713 | Médio — SOL já tem 2024-H2 em v3 (implícito cross-window para SOL) |

### Status especial

| Combo | Observação |
|---|---|
| v2 Bollinger long (4 combos) | Schema pre-v3, sem source_tag/cross-window docs. Débito técnico ADR-0096 inclui auditoria Padrão 25 como parte da normalização. |

## Priorização de rescue tests (EV/custo)

**Critério de triagem:** priorizar combos onde (a) risco é mais alto e (b) janela de teste adicional está disponível nos datasets ingeridos.

Datasets disponíveis: BTC/SOL/ETH 1h têm 2024-H1, 2024-H2, 2025-H1, 2025-H2. LINK/DOT/AVAX 1h têm 2024-H2, 2025-H1, 2025-H2 (ADR-0095 ingest).

### Tier 1 — crítico (testar primeiro)

1. **v7 ETH 2024-H2 long (Série CZE.1)** — único long do stack, trade count no floor. Testar em 2025-H1 (mesmo ativo). Se FAIL, v7 é candidato a rollback imediato (mais risky pq long-side é rara).
2. **v6 SOL 2025-H1 short+trend (Série CZE.2)** — testar em 2024-H2 (mesmo ativo). SOL 2024-H2 já está em v3 Bollinger short+width (Sh=1.38), então regime é amigável a short; se trend_htf falhar lá, expõe filter window-specific.

### Tier 2 — alto (testar segundo)

3. **v4a BTC 2025-H1 short+width (Série CZE.3)** — testar em 2024-H2. BTC 2024-H2 bull forte pode ser regime hostil; preparar para FAIL direcional "esperado" mas distinguir de edge ausente.
4. **v3 BTC 2025-H1 Bollinger short+width** — testar em 2024-H2 (Série CZE.4).
5. **v3 ETH 2025-H1 Bollinger short+width** — testar em 2024-H2 (Série CZE.5).

### Tier 3 — deferido

6. v3 SOL 2024-H2 Bollinger — tem companion SOL 2025-H1 em mesmo manifest (cross-window implícito SOL em v3). Se v3 SOL 2025-H1 passar Tier 2 implícito, ambos consolidados. Deferido.
7. v3 SOL 2025-H1 Bollinger — mesma lógica.
8. v2 Bollinger long — bloqueado por normalização schema (ADR-0096). Faz parte daquele débito.

## Plano de execução

**Série CZE (5 runs Tier 1+2):** 1 run por combo crítico, testando janela adicional. ~10-12min total.

| Tag | Combo | Janela adicional | Dataset |
|---|---|---|---|
| CZE.1 | v7 ETH long+width | 2025-H1 | ethusdt_1h_20250105_20250704 |
| CZE.2 | v6 SOL short+trend | 2024-H2 | solusdt_1h_20240705_20241231 |
| CZE.3 | v4a BTC short+width | 2024-H2 | btcusdt_1h_20240705_20241231 |
| CZE.4 | v3 BTC Bollinger short+width | 2024-H2 | btcusdt_1h_20240705_20241231 |
| CZE.5 | v3 ETH Bollinger short+width | 2024-H2 | ethusdt_1h_20240705_20241231 |

Mesmo gate pré-registrado CZD:
- PASS: Sh ≥ 1.0 (mesmo que outros gates FAIL, é replicação suficiente)
- FAIL strong (Sh < 0): regime flip → candidato rollback
- FAIL marginal (0 ≤ Sh < 1): documenta fragilidade, decisão caso-a-caso

## Riscos antecipados

1. **Regime direcional 2024-H2 bull:** short combos testados em 2024-H2 devem performar pior. Distinguir "FAIL esperado por regime" (hipótese: Sh entre 0 e 1) vs "FAIL por window-specific fluke" (Sh < 0 forte, tipo LINK).
2. **v7 ETH long é o mais sensível:** se CZE.1 ETH 2025-H1 long+width FAIL, stack fica sem long RSI — só long Bollinger v2 (schema velho) sobra.
3. **v3 tem 4 combos** — se CZE.4 e CZE.5 FAIL ambos, v3 pode precisar rollback parcial similar a v8→v8.1.

## Decisão

Executar CZE 5 runs sequencialmente. Closeout em ADR-0108 com matriz de decisão:
- Tier 1 FAIL → rollback imediato (mesmo pattern de v8→v8.1)
- Tier 2 FAIL → shadow/staging até janela extra disponível
- 5/5 PASS → stack consolidado, Padrão 25 cumprido ex-post

**Sem bridge post até closeout** — testes podem confirmar combos atuais, apenas mudar se houver rollback.

## Critério de sucesso desta ADR

1. ✅ Inventário completo dos 13 combos
2. ✅ Triagem priorizada por risco
3. ✅ Plano CZE 5 runs pré-registrado
4. ⏳ Executar CZE
5. ⏳ ADR-0108 closeout
6. ⏳ STATE.md atualizado
