# 0164 — Fase B pré-reg: AVAX cross-window 2025-H2

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário ("OK SIM") + agente
**Relates to:** ADR-0163 (Fase A survivors)

## Hipótese

2 survivors Fase A (AVAX rsi+width Sh=1.64; AVAX rsi+trendhtf Sh=1.77) precisam replicar em janela independente para validar que edge é estrutural (não 2025-H1-específico).

## Probes (2 runs)

| Tag | Combo | Dataset | 2025-H1 Sh |
|---|---|---|---:|
| DD.1 | AVAX rsi 30/70 + width short | 2025-H2 | 1.64 (gate) |
| DD.2 | AVAX rsi 30/70 + trendhtf short | 2025-H2 | 1.77 (gate) |

## Gate pré-registrado

Padrão 40 cross-window: ≥1 janela ≠ da original com Sh ≥ 0.8 E trades ≥ 40.

- **Upgrade convergente**: AMBOS DD.1 e DD.2 passam → Fase C (cross-era 2024)
- **Parcial**: 1 passa, 1 falha → continuar só com o que passa para Fase C
- **Refutação**: 0/2 passa → AVAX era-específico, arquivar frente

Bar Sh≥0.8 é conservador para não-degradação (abaixo do 1.5 de Fase A por ser walk-forward já custeado).

## Não-alvo

- Não variar params — canônicos herdados
- Não ingestir 2024 ainda (Fase C se passar)

## Ação

- Script reutilizar pattern DC com dataset 2025-H2
- Closeout ADR-0165
