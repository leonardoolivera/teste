# 0144 — Série CZ14 pré-registro: Bollinger num_std sensibilidade primeira janela

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0134 (CZ10 RSI bounds análogo), Padrão 38 (bounds extreme candidato), Padrão 40 (cross-era)

## Motivação

Família Bollinger tem 3 manifests live usando `num_std=1.5` canônico (tanto engine quanto filter width). RSI CZ10 revelou que bounds extreme (25/75 vs 30/70) podia dobrar Sharpe em 1 janela — análogo para Bollinger seria `num_std` mais apertado (ex 1.2) ou mais largo (ex 2.0).

Nunca testado manifest-faithful. Hipótese fresca análoga ao CZ10.

## Escopo

3 combos top da família × 2 variantes num_std (apertado 1.2 e largo 2.0) = 6 runs. Primeira janela apenas (screening, não promoção).

| Tag | Combo | Janela | num_std | Baseline Sh (1.5) |
|---|---|---|---:|---:|
| CZ14.1 | SOL Bollinger short + width (w=20, long=False) | 2025-H1 | 1.2 | 2.71 |
| CZ14.2 | SOL Bollinger short + width (w=20, long=False) | 2025-H1 | 2.0 | 2.71 |
| CZ14.3 | ETH Bollinger short + width (w=20, long=False) | 2025-H1 | 1.2 | 2.40 |
| CZ14.4 | ETH Bollinger short + width (w=20, long=False) | 2025-H1 | 2.0 | 2.40 |
| CZ14.5 | SOL Bollinger long + width (w=30, long=True) | 2024-H2 | 1.2 | 2.40 |
| CZ14.6 | SOL Bollinger long + width (w=30, long=True) | 2024-H2 | 2.0 | 2.40 |

Engine num_std varia; filter width mantém num_std=1.5 canônico (isola variável).

## Gate pré-registrado (primeira janela apenas)

- **Upgrade candidato**: ≥2/6 runs com Sh > baseline + 0.5 (equivalente a +0.5 lift primária) → abrir CZ15 cross-window
- **Signal ambíguo**: 1/6 com lift > 0.5 → documentar outlier, não seguir
- **Refutação screening**: 0/6 com lift ≥ 0.5 → `num_std=1.5` é ótimo local, arquivar hipótese. Novo padrão: bounds canônicos Bollinger são robustos (contraste com RSI onde 25/75 > 30/70 em screening).

Padrão 40 (cross-era) aplica-se apenas **se passar primeira janela**. Este é screening.

Timebox: ~4min (6 runs). Closeout em ADR-0145.

## Não-alvo

- Não variar engine `window` (fixar em 20 ou 30 conforme canônico)
- Não testar num_std extremo (< 1.0 ou > 2.5) sem precedente
- Não mexer filter width (isola variável)
- Não promover sem cross-window (Padrão 25)
