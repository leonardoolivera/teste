# 0138 — Série CZ12 pré-registro: RSI 25/75 3ª janela SOL 2024-H1 chop

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0137 (CZ11 2/2 confirma), Padrão 25 reforço (3ª janela)

## Motivação

Usuário optou C: 3ª janela antes de promover manifests. SOL naked 25/75 e SOL trendhtf 25/75 têm 2/2 PASS regime-compatível. Para elevar confiança a 3/3, testar SOL 2024-H1 chop pré-bull — análogo ao CZF (janela que elevou combos contextual → strict).

## Escopo

2 runs SOL 1h 2024-H1 com bounds 25/75:

| Tag | Combo | Regime |
|---|---|---|
| CZ12.1 | SOL naked 25/75 | 2024-H1 chop pré-bull |
| CZ12.2 | SOL trendhtf 25/75 | 2024-H1 chop pré-bull |

Regime 2024-H1 SOL: chop lateral antes do bull-run de meio-2024 (análogo CZF).

## Gate pré-registrado

Por combo (CZ10 + CZ11 + CZ12 agregados):

- **Promoção autorizada**: 3/3 regime-compatível Sh ≥ 1.0 → atualizar manifest 30/70 → 25/75
- **Staging reforçado**: CZ12 PASS ≥ 0.5 → 3/3 confirma contextual forte, próximo da promoção mas ainda espera decisão usuário
- **Refutação upgrade**: CZ12 Sh < 0.3 → CZ10+CZ11 evidence foi era-2025-específica, rollback candidato, manter 30/70

Timebox: ~3min. Closeout em ADR-0139.
