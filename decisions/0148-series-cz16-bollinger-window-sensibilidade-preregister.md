# 0148 — Série CZ16 pré-registro: Bollinger window sensibilidade primeira janela

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário ("continue") + agente
**Relates to:** ADR-0144/0145 (CZ14 num_std), ADR-0146/0147 (CZ15 cross-window), Padrão 41

## Motivação

CZ14 testou `num_std` sensibilidade (refutado). Variável paralela nunca testada: `window` (período SMA). Canônico Bollinger short usa w=20; long usa w=30. Nunca medido se w=10 (mais rápido, mais sinais) ou w=40 (mais lento, menos sinais) muda edge.

Aplicar Padrão 41: se screening for divergente (1/N forte + resto fails), arquivar sem cross-window. Se convergente (2+ PASS), abrir CZ17.

## Escopo

3 combos top × 2 variantes window = 6 runs primeira janela.

| Tag | Combo | Janela | window | Baseline Sh (w canônico) |
|---|---|---|---:|---:|
| CZ16.1 | SOL Bollinger short ns=1.5 | 2025-H1 | 10 | 2.71 (w=20) |
| CZ16.2 | SOL Bollinger short ns=1.5 | 2025-H1 | 40 | 2.71 (w=20) |
| CZ16.3 | ETH Bollinger short ns=1.5 | 2025-H1 | 10 | 2.40 (w=20) |
| CZ16.4 | ETH Bollinger short ns=1.5 | 2025-H1 | 40 | 2.40 (w=20) |
| CZ16.5 | SOL Bollinger long ns=1.5 | 2024-H2 | 15 | 2.40 (w=30) |
| CZ16.6 | SOL Bollinger long ns=1.5 | 2024-H2 | 45 | 2.40 (w=30) |

## Gate pré-registrado

- **Upgrade convergente**: ≥2/6 com lift > 0.5 → abrir CZ17 cross-window (Padrão 41 permite)
- **Signal divergente**: 1/6 com lift > 0.5 → Padrão 41 bloqueia (já validado em CZ15)
- **Refutação screening**: 0/6 com lift ≥ 0.5 → `w=20/30` canônico robusto

Timebox: ~5min. Closeout em ADR-0149.

## Não-alvo

- Não variar num_std (fixar canônico 1.5)
- Não variar filter width (canônico 300/250 bps)
- Não testar window muito extremo (<10 ou >60)
