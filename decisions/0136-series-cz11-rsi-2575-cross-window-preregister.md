# 0136 — Série CZ11 pré-registro: RSI 25/75 cross-window validação (Padrão 25 gate)

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0135 (CZ10 upgrade candidato), Padrão 25, Padrão 38

## Motivação

CZ10 mostrou 3/3 combos top com upgrade Sharpe +1.10 a +1.47 com bounds 25/75. Padrão 25 obriga cross-window antes de promoção. CZ11 testa os 3 combos em janelas adicionais regime-compatíveis.

## Escopo

6 runs (2 janelas adicionais por combo):

| Tag | Combo + bounds | Janela adicional | Regime |
|---|---|---|---|
| CZ11.1 | SOL naked 25/75 | 2024-H2 | bull (regime-oposto, Padrão 26 esperado FAIL) |
| CZ11.2 | SOL naked 25/75 | 2025-H1 | chop |
| CZ11.3 | BTC width 25/75 | 2024-H2 | bull com chop |
| CZ11.4 | BTC width 25/75 | 2025-H2 | misto |
| CZ11.5 | SOL trendhtf 25/75 | 2024-H2 | bull |
| CZ11.6 | SOL trendhtf 25/75 | 2025-H2 | misto |

CZ10 baselines (janela primária 2025-H2 ou 2025-H1):
- SOL naked 2025-H2 25/75: Sh=3.61
- BTC width 2025-H1 25/75: Sh=3.16
- SOL trendhtf 2025-H1 25/75: Sh=2.00

## Gate pré-registrado

Por combo (combinando CZ10 + CZ11):
- **Promoção bounds 25/75**: ≥2/3 janelas regime-compatível Sh ≥ 1.0 + magnitude vs 30/70 baseline preservada (delta ≥ +0.5) → atualizar manifest para 25/75
- **Upgrade window-specific (não promove)**: CZ10 isolado fica como observação; combo permanece 30/70
- **Refutação**: 0/3 janela adicional Sh ≥ 0.5 → CZ10 era window-specific, descartar 25/75

Observação Padrão 26: SOL/BTC em bull (CZ11.1, CZ11.3, CZ11.5) podem FAIL por regime (short em bull); não conta como refutação se filter direcional não está ativo (CZ11.1 SOL naked vai FAIL esperado).

Timebox: ~6min. Closeout em ADR-0137.
