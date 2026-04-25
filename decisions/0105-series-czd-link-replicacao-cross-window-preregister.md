# 0105 — Série CZD pré-registro: LINK RSI short replicação cross-window (2025-H1, 2024-H2)

**Status:** Accepted — pré-registro
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0098 (CZ closeout + v8), Padrão 20 seletivo, Padrão 24 (dataset split)

## Hipótese

LINK 2025-H2 passou com Sh=1.760 (CZ.3), entrou em v8. Mas 1 janela não garante edge estrutural. Se LINK 2025-H1 e/ou 2024-H2 também passarem, LINK vira combo de alta confiança (replicação temporal 2+ janelas). Se só 1 passar, edge é janela-específico.

Aplicar Padrão 24: variação de dataset (janela temporal) é teste real de robustez vs `mc_seed` que só varia bootstrap.

## Design (2 runs)

Mesma config exata que CZ.3 (RSI short naked, params v8):
- strategy: rsi (window=14, oversold=30, overbought=70)
- short-only, fixed_notional=2000, seed=42, mc_resamples=1000
- 5-fold rolling, train_fraction=0.5
- cost stress: fee+10, spread+10

| Tag | Window | Dataset | Expectativa |
|---|---|---|---|
| CZD.1 | 2025-H1 | linkusdt_1h_20250105_20250704 | Sh ≥ 1.0 se edge persistente |
| CZD.2 | 2024-H2 | linkusdt_1h_20240705_20241231 | Sh ≥ 1.0 se edge persistente |

Total: 2 runs (~4min).

## Gates pré-registrados

### Gate 1 — Replicação 2/2
PASS se ambas janelas Sh ≥ 1.0. **Cenário ideal:** LINK vira combo high-confidence 3-window (2024-H2, 2025-H1, 2025-H2), candidato a entrar em v9 com flag de robustez temporal.

### Gate 2 — Replicação 1/2
PASS contextual. LINK edge existe mas é janela-específico. Decisão:
- Se janela que passa é 2025-H1 (mais próxima de H2): reforça que edge é do "2025 regime" crypto, não estrutural
- Se janela que passa é 2024-H2: edge intermitente, v8 mantém LINK mas documenta fragilidade
- Se nenhuma passa: v8 pode ter sido fluke 2025-H2 específico

### Gate 3 — Replicação 0/2
FAIL. LINK 2025-H2 foi janela única favorável. Decisão:
- **Não retira v8** (não depreca combo ativo por teste futuro post-hoc sem predeclaração estrita)
- Documenta fragilidade e adiciona "window-specific edge" à descrição do combo
- Bloqueia adição de mais combos LINK até nova janela disponível

### Gate 4 — cost_r
Se cost_r < 0.95 em ambas janelas, indica problema estrutural LINK liquidez (não só 2025-H2).

## Riscos antecipados

1. **2024-H2 regime bull forte**: short-side pode ter FAIL estrutural por direção contrária ao regime (BTC +180% 2024-H2). Se CZD.2 FAIL, verificar se é por regime direcional (esperado) ou por edge ausente (sinal).
2. **2025-H1 consolidação**: período pré-rally 2025-H2, pode ter vol baixa que degrade RSI mean-reversion. Se Sh cai para 0.5-0.9 zone, edge existe mas enfraquecido.
3. **Trade count**: janelas de 6 meses a 1h dão ~4320 bars. Fold count 5 = ~864 bars por fold. Trade count deve ser similar ao CZ.3 (84). Se cai para < 30, fold granularity insuficiente.

## Interpretação esperada

| CZD.1 (2025-H1) | CZD.2 (2024-H2) | Ação |
|---|---|---|
| PASS | PASS | LINK high-confidence 3-window, candidato v9 flag |
| PASS | FAIL | Edge 2025-regime, v8 mantém com robustez 2-window documentada |
| FAIL | PASS | Edge intermitente, v8 mantém fragilidade documentada |
| FAIL | FAIL | LINK 2025-H2 window-specific, v8 mantém mas bloqueia extensão |

## Critério de sucesso desta ADR

1. 2 runs executados (CZD.1, CZD.2)
2. ADR-0106 closeout documenta verdict
3. Decisão sobre confiança em combo LINK v8 baseada em matriz
4. STATE.md atualizado
