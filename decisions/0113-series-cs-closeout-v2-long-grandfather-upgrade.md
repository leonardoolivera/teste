# 0113 — Série CS closeout: v2 long grandfather replicação (BTC upgrade, SOL flag)

**Status:** Accepted — replicação mista
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0112 (pré-registro), ADR-0111 (schema norm), Padrão 25/26

## Resultado CS (4 runs, bollinger long 30/1.5 + width 250)

| Tag | Combo | Test window | Trades | Sharpe | PnL% | MDD% | Verdict |
|---|---|---|---:|---:|---:|---:|---|
| CS.1 | BTC 2024-H2 baseline | 2024-H1 | 27 | **0.500** | 1.05 | 1.65 | contextual |
| CS.2 | BTC 2024-H2 baseline | 2025-H1 | 20 | **2.087** | 3.68 | 1.38 | **strict** |
| CS.3 | SOL 2024-H2 baseline | 2024-H1 | 41 | 0.183 | 0.56 | 4.14 | status quo |
| CS.4 | SOL 2024-H2 baseline | 2025-H1 | 46 | **-0.145** | -0.70 | 5.17 | rollback flag |

## Classificação final

### BTC 2024-H2 → **STRICT UPGRADE**
- CS.2 2025-H1: Sh=2.09, 20 trades, PnL +3.68% — forte replicação
- CS.1 2024-H1: Sh=0.50 (borderline contextual), 27 trades — marginal mas não refutatório
- Gate strict (≥1 janela Sh≥1.0 + trades≥20) atendido via CS.2

Combo sai de `single_window` → `strict (CS.2)` + `contextual (CS.1)`.

### SOL 2024-H2 → **GRANDFATHER MANTIDO + FLAG**
- CS.3 2024-H1: Sh=0.18 (status quo) — edge inexistente, 41 trades não salvam
- CS.4 2025-H1: Sh=-0.14 (rollback flag) — PnL negativo, edge refutado em janela chop
- Baseline SOL 2024-H2 Sh=2.40 permanece válido, mas edge é altamente específico a 2024-H2

Não removemos combo do stack automaticamente (single incidente negativo, sem perda catastrófica). Mas:
- **Flag de risco** adicionado ao manifest
- **Prioridade de revisão** elevada em próximas auditorias
- Se surgirem FAILs adicionais (ex: paper degradação ou re-teste com diferentes seeds), candidato #1 a remoção

## Padrão 27 (NOVO): grandfather replication outcomes diverge by combo

CS demonstra que replicação cross-window de combos grandfather pode:
1. **Confirmar edge** (BTC: agora strict-validated com evidence em 2 janelas)
2. **Refutar edge** (SOL: 2/2 janelas adicionais FAIL/marginal — edge de 2024-H2 pode ser regime-específico narrow)

**Não assumir** que combos grandfathered por v1 protocolo são auto-equivalentes a strict modernos. Re-teste regime-matched é informativo mesmo quando o combo já estava em live — e pode flagar risco prematuro.

## Ação executada

1. ✅ `bollinger_width_regime_20260418_v2.json` atualizado:
   - BTC 2024-H2: `strict (CS.2 Sh=2.09) + contextual (CS.1 Sh=0.50)`
   - SOL 2024-H2: `single_window` + flag ROLLBACK
   - Adicionado `grandfather_replication_adr` e `grandfather_replication_at`
2. ✅ ADR-0113 closeout (este documento)
3. ⏳ STATE.md entry (próximo)

## Bridge post

**Não.** Edit de metadata; nenhum combo removido, nenhum notional alterado, nenhuma mudança em live_status. SOL flag é info interna pra próxima auditoria.

Se futura série adicionar evidência refutatória sobre SOL 2024-H2 v2, aí sim bridge post com proposta de remoção.

## Stack pós-CS

13 combos, mesma composição. Classificações:
- **Strict**: 5 (v8.1 BTC+SOL 2025-H2, v4a BTC 2025-H1, v3 SOL 2024-H2+2025-H1 pair, **v2 BTC 2024-H2 [NEW upgrade]**)
- **Contextual**: 4 (v7 ETH 2024-H2, v6 SOL 2025-H1, v3 BTC 2025-H1, v3 ETH 2025-H1)
- **Cross-window via companion**: 2 (v2 ETH 2024-H1, v2 ETH 2025-H1)
- **Single window + grandfather flag**: 1 (v2 SOL 2024-H2)
- **Single window grandfather clean**: 0

Qualidade do stack melhorou: 1 upgrade strict, 1 flag identificado. Zero combos perdidos.
