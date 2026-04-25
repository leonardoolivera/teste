# 0134 — Série CZ10 pré-registro: RSI bounds sensibilidade nos top combos (25/75, 35/65)

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0131 (família trend-following encerrada), backlog "otimização mean-reversion"

## Motivação

Com família trend-following arquivada (CZ6-9), próximo ângulo de melhoria do stack é otimização dos combos existentes. RSI bounds (overbought/oversold) é parâmetro nunca testado em sensibilidade — todos combos canônicos usam 30/70. Hipótese: thresholds mais extremos (25/75) reduzem trades mas elevam quality (entries em condições mais raras), thresholds mais frouxos (35/65) aumentam trades mas potencialmente diluem edge.

Sweet spot pode existir por combo. Se sim, oportunidade de upgrade Sharpe sem mudar engine ou stack composition.

## Escopo

2 combos top-3 do stack × 2 variantes bounds × baseline = 6 runs, 1h:

| Tag | Combo | Bounds | Baseline canônico |
|---|---|---|---:|
| CZ10.1 | SOL 2025-H2 short naked (v8.1) | 25/75 | 30/70 = 2.30 |
| CZ10.2 | SOL 2025-H2 short naked (v8.1) | 35/65 | 30/70 = 2.30 |
| CZ10.3 | BTC 2025-H1 short + width (v4a) | 25/75 | 30/70 = 1.69 |
| CZ10.4 | BTC 2025-H1 short + width (v4a) | 35/65 | 30/70 = 1.69 |
| CZ10.5 | SOL 2025-H1 short + trend_htf (v6) | 25/75 | 30/70 = ~0.89 |
| CZ10.6 | SOL 2025-H1 short + trend_htf (v6) | 35/65 | 30/70 = ~0.89 |

## Gate pré-registrado

Decisão por combo (não agregado):
- **Upgrade canônico**: variante mostra Sh ≥ baseline + 0.3 com trades ≥ 25 (não dilui sample) → propor mudança bounds no manifest
- **Sweet spot existe mas não promove**: variante mostra Sh ≥ baseline + 0.1 mas trades < 25 → registro como observação, não muda manifest
- **Bounds canônico ótimo**: nenhuma variante > baseline + 0.1 → confirmar 30/70 como default, fechar sensibilidade

Risk: se 35/65 ganha em 1+ combo, abre questão "trades > 30 garante mais robustez?" — discutir caso surja.

Timebox: ~6min. Closeout em ADR-0135.
