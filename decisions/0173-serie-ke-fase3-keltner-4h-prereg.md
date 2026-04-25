# 0173 — Série KE Fase 3 pré-reg: Keltner 4h timeframe

**Status:** Pre-registered — piloto automático (ADR-0172 fechou 1h).
**Date:** 2026-04-20
**Deciders:** Usuário (piloto automático) + agente
**Relates to:** ADR-0170/0171/0172 (Keltner 1h refutado), Padrão 40 (cross-era)

## Hipótese

Keltner 1h refutado em 12 runs (ADR-0172). Hipótese estrutural "ATR robusto vs stdev" falhou em 1h porque vol em crypto 1h é **persistente** (não spiky). **4h** deveria ter propriedades diferentes:

- Menos tick-level noise → ATR mais estável
- Estruturas de vol médias mais claras (breakouts/ranges duram horas, não minutos)
- Se ATR adiciona edge genuíno vs stdev, deveria aparecer em 4h antes de 1h

Prior: moderadamente pessimista. BB 4h também é ativa na pesquisa histórica (ADR-0140 canonizou trend_htf 4h); se ATR diferenciasse, já teria aparecido em experimentos similares. Mas **dimensão não-explorada** é barata e vale testar.

## Probes (3 runs)

| Tag | Combo | Dataset |
|---|---|---|
| KE.13 | Keltner 20/14/2.0 short 4h | BTC 2025-H1 |
| KE.14 | Keltner 20/14/2.0 short 4h | ETH 2025-H1 |
| KE.15 | Keltner 20/14/2.0 short 4h | SOL 2025-H1 |

## Gate

- **Pass**: ≥2/3 Sh ≥ 1.5 AND trades ≥ 30 → Fase 3b cross-window 2025-H2
- **Padrão 41**: 1/3 → bloqueia
- **Refutação**: 0/3 → arquivar Keltner em todos timeframes; passar para Candidato A (zscore) ou próxima frente

## Não-alvo

- Não testar 4h + filter nesta fase (primeiro confirmar edge naked)
- Não testar long-only (simetria com 1h)
- Não alterar params (window=20, atr_period=14, mult=2.0 canônicos)

## Ação

- Script `tools/run_ke_4h_sweep.py`
- Closeout em ADR-0174
