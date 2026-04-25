# 0150 — Série CZ17 pré-registro: width filter min_width_bps sensibilidade

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário ("pode fazer") + agente
**Relates to:** ADR-0144/0148 (CZ14/CZ16 BB sensibilidade), Padrão 42 (window ótimo local), Padrão 41 (variance screening)

## Motivação

Filter `bollinger_width:min_width_bps=N` usado em 5+ manifests live (v4a, bollinger_short_width, bollinger_width_regime v2, rsi_long_width_eth). Canônicos: 250 (long) e 300 (short). Nunca testado se threshold mais baixo (capta regimes menos voláteis) ou mais alto (só ultra-volátil) muda edge.

## Escopo

3 combos top × 2 variantes min_width_bps = 6 runs primeira janela. Canônicos intactos como baseline.

| Tag | Combo | Janela | min_width_bps | Canônico |
|---|---|---|---:|---:|
| CZ17.1 | SOL short ns=1.5 w=20 | 2025-H1 | 150 | 300 |
| CZ17.2 | SOL short ns=1.5 w=20 | 2025-H1 | 500 | 300 |
| CZ17.3 | ETH short ns=1.5 w=20 | 2025-H1 | 150 | 300 |
| CZ17.4 | ETH short ns=1.5 w=20 | 2025-H1 | 500 | 300 |
| CZ17.5 | SOL long ns=1.5 w=30 | 2024-H2 | 125 | 250 |
| CZ17.6 | SOL long ns=1.5 w=30 | 2024-H2 | 400 | 250 |

Filter internal params (window=30, num_std=1.5) fixos; apenas `min_width_bps` varia.

## Gate pré-registrado

- **Upgrade convergente** (Padrão 41 aplica): ≥2/6 com lift > 0.5 → abrir CZ18 cross-window
- **Signal divergente**: 1/6 com lift > 0.5 → arquivar, Padrão 41 bloqueia
- **Refutação screening** (Padrão 42 expansão): 0/6 lift ≥ 0.5 → canônicos robustos, novo corolário Padrão 42 sobre filter thresholds

Timebox: ~5min. Closeout em ADR-0151.

## Não-alvo

- Não variar engine params (fixar canônico)
- Não testar thresholds extremos (< 100 ou > 600)
- Não abrir cross-window sem gate convergente
