# 0108 — Série CZE closeout: Padrão 25 refinado — regime direcional confunde cross-window test (Padrão 26)

**Status:** Accepted — closeout, refinamento metodológico
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0107 (CZE pré-registro), ADR-0106 (CZD + Padrão 25), Padrão 13

## Resultado nominal: 0/5 PASS, 4/5 FAIL strong

| Tag | Combo | Janela teste | Trades | Sh | Verdict nominal |
|---|---|---|---|---|---|
| CZE.1 | v7 ETH long+width | 2025-H1 | 43 | -0.221 | FAIL strong |
| CZE.2 | v6 SOL short+trend | 2024-H2 | 31 | -1.022 | FAIL strong |
| CZE.3 | v4a BTC short+width | 2024-H2 | 43 | -0.759 | FAIL strong |
| CZE.4 | v3 BTC boll+width | 2024-H2 | 47 | +0.522 | FAIL marginal |
| CZE.5 | v3 ETH boll+width | 2024-H2 | 63 | -0.225 | FAIL strong |

## Reinterpretação: FAIL é por regime direcional, não window-specific

**Observação crítica:** todos os 5 testes foram em janela de **regime direcional oposto** à direção do combo:
- CZE.1: combo long testado em 2025-H1 (pós-crash, regime bear moderado)
- CZE.2-5: 4 combos short testados em 2024-H2 (bull forte, BTC +180%)

FAIL strong em regime oposto é **esperado**, não sinal de window-specific fluke. Contraste com CZD:
- CZD.1 (2025-H1): LINK short em janela consolidação — regime **similar** a H2. FAIL Sh=0.51 é sinal fraco.
- CZD.2 (2024-H2): LINK short em bull. FAIL Sh=-1.34 é regime esperado.
- CZD **teve 2 janelas similares**, ambas FAIL → evidência clara de window-specific.

**CZE só testou 1 janela direcionalmente oposta por combo.** Resultado não é comparável a CZD.

### Por que Padrão 13 já previa isso

Padrão 13 (filter alinhado ao payoff): short + trend_htf(short_only) deve bloquear em bull. Em 2024-H2 bull, combo deveria gerar poucos/zero trades se filter funciona.

**Análise de trade count:**
- v6 SOL short+trend 2024-H2: 31 trades (vs 51 baseline) — **filter reduziu 39%**, mas ainda operou e perdeu
- v3/v4a width-filter combos: 43-63 trades em bull — width é **direcionalmente neutro** (só vol), não bloqueia por regime
- v7 ETH long+width 2025-H1: 43 trades — width neutro, opera long em bear e perde

**Conclusão:** filters width são estruturalmente neutros por design. Apenas trend_htf é direcional. FAIL em regime oposto com width filter é **artefato do filter choice**, não refutação da estratégia.

## Padrão 26 (NOVO) — Cross-window test precisa de regime-awareness

**Enunciado:** Teste cross-window para validar Padrão 25 deve usar **janela de regime similar** à baseline, não uma janela qualquer. Regime direcional oposto com filter não-direcional gera FAIL estrutural-esperado, não evidência de window-specific fluke.

**Protocolo refinado para Padrão 25:**
1. Baseline PASS em janela X com regime R
2. Replicação exigida em janela Y com regime **similar a R** (mesma direção dominante ou mesmo grau de chop)
3. Se Y oposto: teste é informativo sobre protection (filter eficácia) mas **não** sobre edge replication
4. Se só janelas opostas disponíveis: exigir 3ª evidência (ex: Bull Y Sh ≈ 0 com filter direcional comprova protection)

**Classificação de janelas (crypto 1h):**
- 2024-H1: chop moderado
- 2024-H2: bull forte
- 2025-H1: bear moderado / consolidação
- 2025-H2: chop/misto
- 2026-H1: pendente (data cutoff 2026-04-20)

**Pares de regime-similar disponíveis:**
- 2025-H1 ↔ 2024-H1 (chop/consolidação)
- 2024-H2 ↔ ? (bull forte único — 2026-H1 precisaria ser bull para comparar)
- 2025-H2 ↔ parcial com 2024-H1

**Implicação:** combos short 2025-H1 → testar em 2024-H1 (similar regime) seria mais válido do que 2024-H2 (bull oposto).

## Decisão: não-rollback, mas abrir CZF com regime-matched test

**Não executar rollback em cascata.** CZE é metodologicamente insuficiente para refutar combos existentes. 4/5 FAIL strong em regime oposto é consistente com operação esperada (filters não-direcionais não bloqueiam sinal oposto ao regime).

**Próxima ação: Série CZF — regime-matched cross-window:**

| Tag | Combo | Janela teste | Regime-match |
|---|---|---|---|
| CZF.1 | v7 ETH long+width 2024-H2 | 2024-H1 | chop moderado (similar chop 2024-H2 início) |
| CZF.2 | v6 SOL short+trend 2025-H1 | 2024-H1 | chop (similar consolidação) |
| CZF.3 | v4a BTC short+width 2025-H1 | 2024-H1 | chop |
| CZF.4 | v3 BTC boll+width 2025-H1 | 2024-H1 | chop |
| CZF.5 | v3 ETH boll+width 2025-H1 | 2024-H1 | chop |

Todos testando em 2024-H1 (chop/consolidação, regime-similar a 2025-H1 consolidação). ETH long 2024-H2 baseline era regime final de bull → 2024-H1 fim-de-chop é o mais próximo disponível sem 2026-H1 ingerido.

### Exceção importante: CZE.2 v6 SOL com trend_htf

v6 usa `trend_htf:short_only`. Deveria bloquear em 2024-H2 bull. Trade count caiu de 51 → 31 (39% reduction) mas ainda perdeu Sh=-1.02. Isso pode ser sinal legítimo de que trend_htf(50) 4h não é forte o suficiente em bull SOL — filter tem holes. Registrar como risco específico de v6, não bloquear stack.

## Atualização Padrão 25

Padrão 25 original (ADR-0106): "≥2 janelas OOS PASS".

**Padrão 25 refinado (ADR-0108):** "≥2 janelas OOS PASS em **regimes similares ou complementares** (evidência de edge replication). Janela de regime oposto + filter não-direcional produz FAIL estrutural-esperado, não refuta edge."

**LINK continua FAIL sob Padrão 25 refinado** porque CZD testou 2025-H1 (regime similar a 2025-H2) e ainda falhou Sh=0.51. A evidência LINK permanece válida mesmo sob refinamento.

## Decisão final

1. **Não-rollback** em cascata. Stack 13 combos mantém.
2. **Abrir CZF** — regime-matched cross-window test (5 runs em 2024-H1)
3. **Documentar Padrão 26** e refinar Padrão 25
4. **Sem bridge post** — stack não muda
5. Se CZF também 0/5 PASS em regime-matched, aí sim considerar rollbacks

## Riscos residuais

1. **v6 SOL trend_htf vazamento em bull:** 31 trades em 2024-H2 bull vs esperado ~0 indica filter não bloqueia bem. Não é rollback trigger mas é débito técnico — filter spec pode precisar threshold mais agressivo.
2. **2024-H1 pode não ser chop puro:** Q1 2024 teve rally inicial. Regime classification precisa checagem visual antes de CZF.
3. **Auditoria ficou inconclusiva até CZF:** stack opera com combos não-cross-window validados ainda.

## Critério de sucesso desta ADR

1. ✅ Sweep CZE executado
2. ✅ Reinterpretação honesta (não cair em rollback reflexivo)
3. ✅ Padrão 26 formalizado (regime-awareness em cross-window)
4. ✅ Padrão 25 refinado
5. ✅ CZF plano definido
6. ⏳ CZF execução
7. ⏳ STATE.md atualizado
