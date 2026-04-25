# 0152 — Série CZ18 pré-registro: RSI period sensibilidade

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário ("SIJM") + agente
**Relates to:** ADR-0149/0151 (CZ16/CZ17 Bollinger), Padrão 42 (ordem exploração: bounds > window > threshold)

## Motivação

RSI `period` canônico 14 nunca testado sistematicamente. Padrão 42 indica window engine (period) como prioridade 2 de sensibilidade (após bounds já explorado em CZ10-13). Testar 7 (rápido) e 21 (lento) em 3 combos top RSI short.

Predição Padrão 42: canônico deve ser ótimo local, period=7 pode colapsar (whipsaw como BB w=10) ou ser neutro (indicador RSI já tem suavização interna diferente de Bollinger).

## Escopo

3 combos top RSI short × 2 variantes period = 6 runs primeira janela.

| Tag | Combo | Janela | period | Canônico Sh |
|---|---|---|---:|---:|
| CZ18.1 | SOL naked 30/70 | 2025-H2 | 7 | 2.30 |
| CZ18.2 | SOL naked 30/70 | 2025-H2 | 21 | 2.30 |
| CZ18.3 | BTC width 30/70 | 2025-H1 | 7 | 1.69 |
| CZ18.4 | BTC width 30/70 | 2025-H1 | 21 | 1.69 |
| CZ18.5 | SOL trendhtf 25/75 | 2025-H1 | 7 | 2.00 |
| CZ18.6 | SOL trendhtf 25/75 | 2025-H1 | 21 | 2.00 |

Bounds mantidos nos canônicos de cada combo (30/70 SOL naked, 30/70 BTC width, 25/75 SOL trendhtf pós-CZ12).

## Gate pré-registrado

- **Upgrade convergente**: ≥2/6 lift > 0.5 → abrir CZ19 cross-window
- **Signal divergente**: 1/6 lift > 0.5 → Padrão 41 bloqueia
- **Refutação screening**: 0/6 lift ≥ 0.5 → canônico period=14 robusto, Padrão 42 validado cross-família

Timebox: ~5min. Closeout em ADR-0153.

## Não-alvo

- Não variar bounds nesta série (isola variável)
- Não testar period < 5 ou > 30 (sem precedente)
- Não mexer filter params
