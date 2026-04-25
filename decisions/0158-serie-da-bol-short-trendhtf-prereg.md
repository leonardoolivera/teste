# 0158 — Série DA pré-reg: Bollinger short + trend_htf filter (filter novo em asset existente)

**Status:** Pre-registered — gate definido antes de rodar.
**Date:** 2026-04-20
**Deciders:** Usuário ("sim") + agente
**Relates to:** ADR-0156/0157 (Padrão 43 — filter > engine), Padrão 42 (canônicos BB robustos)

## Hipótese

Padrão 43 diz: filter diferente diversifica mais que engine. Todos combos BB short atuais usam `bollinger_width` filter. Testar `trend_htf` filter em BB short pode: (a) abrir dimensão nova de edge, (b) aumentar diversificação do stack (bol_short + trendhtf é estruturalmente diferente de bol_short + width).

## Probes (3 runs)

| Tag | Combo | Dataset | Baseline (bol short + width) Sh |
|---|---|---|---:|
| DA.1 | bol_w20_ns1.5 + trend_htf (short) | BTC 2025-H1 | 2.33 |
| DA.2 | bol_w20_ns1.5 + trend_htf (short) | ETH 2025-H1 | 2.40 |
| DA.3 | bol_w20_ns1.5 + trend_htf (short) | SOL 2025-H1 | 2.71 |

Filter: `trend_htf:htf=4h:sma_window=50:mode=short_only` (canônico stack).
Engine: canônico BB short (w=20, ns=1.5, long_only=false).

## Gate pré-registrado

Para cada combo:
- **Upgrade convergente** (2+ runs): lift > +0.5 sh vs width baseline em ≥2/3 assets → Série DB cross-era (2024-H1/H2) + eventual promoção
- **Signal divergente** (Padrão 41): lift > +0.5 em 1/3 apenas → bloqueio, janela-específica
- **Refutação**: 0/3 com lift > +0.5 → filter width permanece superior; descartar trend_htf em BB short

Bar: lift > +0.5 é conservador (≈ movimento 1-sigma de Sharpe walk-forward em 2025-H1).

## Não-alvo

- Não testar trend_htf em BB long (assets 2025 foram majoritariamente short-favorable; BB long canônico usa w=30)
- Não variar params engine — só troca de filter
- Não correlacionar com stack ainda — só após closeout DA

## Ação

- Script `tools/run_da_sweep.py`
- Closeout em ADR-0159
