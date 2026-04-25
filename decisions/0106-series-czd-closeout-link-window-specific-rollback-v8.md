# 0106 — Série CZD closeout: LINK 2025-H2 é window-specific, recomenda rollback v8 (Padrão 25)

**Status:** Accepted — closeout + rollback executed (opção A)
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0098 (v8 promoção LINK), ADR-0105 (CZD pré-registro), Padrão 20, Padrão 24

## Resultado

**1/3 janelas PASS (apenas a baseline que originou o combo). Replicação cross-window 0/2 exclui baseline → FAIL.**

| Tag | Window | Trades | PnL% | MDD% | Sh | MCp5 | cost_r | Verdict |
|---|---|---|---|---|---|---|---|---|
| CZ.3 | 2025-H2 (v8 baseline) | 84 | +11.73 | 5.80 | **1.760** | 10150 | 0.9590 | PASS |
| CZD.1 | 2025-H1 | 80 | +3.01 | 11.97 | 0.512 | 9064 | 0.9587 | FAIL (Sh, MCp5) |
| CZD.2 | 2024-H2 | 72 | **-11.70** | 18.21 | **-1.336** | 6422 | 0.9554 | FAIL strong |

### Achado principal: LINK 2025-H2 não é edge estrutural

O Sh=1.76 que colocou LINK em v8 **não se replica** em janelas adjacentes:
- **2025-H1:** Sh cai para 0.51 (queda de -1.25 σ). Mesmo tipo de mercado (consolidação pré-rally), sem inversão de regime.
- **2024-H2:** Sh=-1.34 (inversão completa, -3.1 σ vs H2). Regime bull forte (BTC +180%) pune short — esperado, mas intensidade confirma que estratégia não tem proteção.

**cost_r estável cross-window (~0.958)** — custo LINK é estrutural e não é o problema principal. O problema é o edge direcional.

### Contraste com BTC e SOL em v8

BTC e SOL tiveram validação mais rigorosa histórica (v3 inclui múltiplas janelas via ADRs anteriores). LINK entrou em v8 com **1 janela única validada**. CZD expõe que essa promoção foi precipitada.

## Padrão 25 (NOVO) — Promoção com 1 janela única tem taxa de falha alta

**Enunciado:** Combos promovidos com base em **1 janela OOS única** (sem cross-window replication prévia) têm risco elevado de ser window-specific fluke. CZD mostra LINK 2025-H2 Sh=1.76 → -1.34 em janela adjacente 2024-H2.

**Evidência:**
- LINK v8 entrou com CZ.3 2025-H2 apenas → CZD revela 1/3 cross-window
- Contraste: BTC/SOL v3 tiveram validação múltipla antes de entrar em stack

**Implicação:** antes de promover combo novo ao stack ativo, requer ≥2 janelas OOS com PASS independente. Se só 1 janela disponível (ex: ingest recente), combo entra em **shadow/staging** não em stack ativo — até segunda janela confirmar.

**Ação retrospectiva:** auditar outros combos do stack promovidos com janela única. Se houver, marcar como "shadow" e validar cross-window antes de reafirmar.

## Decisão: rollback LINK de v8

### Recomendação técnica
1. **Depreciar v8** (`rsi_short_pure_2025h2_20260420.json`) — marca `superseded_by: v8.1`, reason: "LINK cross-window FAIL (ADR-0106)"
2. **Emitir v8.1** como cópia de v8 **sem LINK** (só BTC+SOL, igual v3 mas mantendo schema v3 padrão)
3. **Bridge post:** mudança de stack (LINK sai) exige post — quebra regra signal-only porque afeta decisão ativa do bot

### Risco de NÃO rollback
Manter LINK em v8 significa stack ativa contém combo que **não tem edge estrutural provado**. Se bot estiver paper-trading v8, ele está apostando em fluke. Risco: próxima janela (2026-H1) pode replicar 2024-H2 pattern.

### Risco de rollback
Post-hoc modification de stack ativa é pesado. Porém:
- CZD foi **pré-registrado** (ADR-0105) com matriz de gates antes da execução
- Gate 3 (0/2 replicação) foi pré-definido como "não retira v8 por precaução contra post-hoc sem predeclaração estrita"
- Mas **2024-H2 Sh=-1.34 é muito forte** (não marginal FAIL) e **2025-H1 também FAIL** → evidência exceede o que ADR-0105 assumiu como cenário típico

ADR-0105 Gate 3 dizia "não retira, documenta e bloqueia extensão". Mas assumia FAILs marginais (Sh 0.6-0.9). Sh=-1.34 é regime flip completo, não fragilidade. **Recomendo atualizar ADR-0105 retroativamente** e executar rollback.

### Decisão: opção A executada

Usuário confirmou opção A (rollback completo). Executado em 2026-04-20T06:00Z:
- Emitido `exports/approved/rsi_short_pure_2025h2_20260420b.json` (v8.1, 2 combos BTC+SOL)
- v8 marcado `live_status: superseded`, `superseded_by: v8.1`, `superseded_reason` com dados CZD
- Bridge post em `inbox_botbinance.md` instruindo remoção v8 / adição v8.1 / encerramento paper-trade LINK
- Stack pós-rollback: 13 combos

## Impacto em Padrão 20

Padrão 20 refinado (ADR-0098): "short-side edge é seletivo cross-universe, 3/6 ativos PASS em 2025-H2".

**Atualização pós-CZD:** seletivo **cross-asset** confirmado; **cross-window** é separado e mais rigoroso. LINK passou cross-asset mas falhou cross-window. BTC/SOL têm cross-window validado em v3.

**Padrão 20 final:** edge short-side é tanto asset-specific quanto window-specific. Requer validação em **ambas dimensões** antes de promoção a stack ativo.

## Lições para futuras promoções

1. **Dataset split variation** (Padrão 24) deve ser pré-registrado ANTES da promoção, não depois
2. **2+ janelas OOS PASS** é o novo gate mínimo para adicionar combo ao stack ativo
3. **Novos ingests** vão para "staging" antes de stack ativo
4. Auditar combos atuais do stack por Padrão 25 — quais foram promovidos com 1 janela única?

## Próximos passos

1. **Aguardar confirmação usuário** sobre rollback v8 → v8.1 (opção A, B ou C)
2. Se rollback: emitir `rsi_short_pure_2025h2_20260420b.json` ou `..._20260420_v2.json`, bridge post
3. Auditar outros combos do stack (v2 long, v4a, v6, v7) por janela única
4. STATE.md atualizado

## Critério de sucesso desta ADR

1. ✅ Sweep CZD executado (2 runs)
2. ✅ Closeout documenta 1/3 replicação cross-window
3. ✅ Padrão 25 formalizado
4. ⏳ Decisão de rollback aguarda usuário
5. ⏳ STATE.md atualizado (próximo)
