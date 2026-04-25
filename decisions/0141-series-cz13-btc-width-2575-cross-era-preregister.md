# 0141 — Série CZ13 pré-registro: BTC width 25/75 3ª janela cross-era

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0135 (CZ10), ADR-0137 (CZ11), ADR-0140 (SOL trendhtf promovido), Padrão 40

## Motivação

CZ10 descobriu BTC width 25/75 Sh=3.16 (vs 1.69 baseline 30/70). CZ11 cross-window deu 1 strict (2025-H1 primária) + 1 fraco (2025-H2 Sh=0.45). Ficou em limbo — não promovido, não refutado.

Padrão 40 (cross-era) exige ≥1 janela 2024 + ≥1 janela 2025 com Sh ≥ 1.0. Temos 2025-H1 OK, 2025-H2 fraco. Falta 2024 pra fechar decisão.

Alpha forge análogo a CZ12 (fechou SOL trendhtf + refutou SOL naked).

## Escopo

2 runs BTC 1h com bounds 25/75 + filter width (`bollinger_width:window=30:num_std=1.5:min_width_bps=250`):

| Tag | Combo | Janela | Regime |
|---|---|---|---|
| CZ13.1 | BTC width 25/75 | 2024-H1 | chop pré-bull |
| CZ13.2 | BTC width 25/75 | 2024-H2 | bull |

## Gate pré-registrado

Agregado CZ10 + CZ11 + CZ13 (3/3+ janelas):

- **Promoção autorizada**: ≥3 janelas regime-compatível Sh ≥ 1.0 → atualizar manifest BTC width para 25/75
- **Staging reforçado**: CZ13 PASS ≥ 0.5 mas 2025-H2 segue fraco → documentar como edge instável, não promover
- **Refutação upgrade**: CZ13 Sh < 0.3 em 2024-H1 chop (regime-compatible) → rollback candidato, BTC width fica em 30/70

2024-H2 bull é regime-incompatível com short: Sh negativo esperado por Padrão 26, não conta contra o gate (sanity check que filter segue contendo bull como design).

Timebox: ~3min. Closeout em ADR-0142.

## Não-alvo

- Não testar BTC naked 25/75 (já refutado implicitamente em CZ10 — width é load-bearing)
- Não tocar SOL combos (escopo CZ12 fechado)
- Não mudar bounds além de 25/75
