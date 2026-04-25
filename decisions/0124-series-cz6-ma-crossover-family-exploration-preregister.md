# 0124 — Série CZ6 pré-registro: MA Crossover family exploration (20/50 long)

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0117 (CY Donchian refutado), Padrão 29

## Motivação

Stack 13 combos dominado por RSI + Bollinger (mean-reversion). Donchian (breakout) refutado em CY como anti-diversificador (Padrão 29). MA Crossover é a segunda engine trend-following canônica não testada. Hipótese: se MACX 20/50 long mostra Sharpe ≥ 0.5 em ≥3/6 probes (mesma barra CY), vira candidato real a diversificador; se reprovar, fecha a classe trend-following para 1h.

## Escopo

6 runs, MA Crossover 20/50 long, mesma matriz CY:

| Tag | Asset | Janela | Regime |
|---|---|---|---|
| CZ6.1 | BTC | 2024-H2 | bull com chop |
| CZ6.2 | ETH | 2024-H2 | bull com chop |
| CZ6.3 | SOL | 2024-H2 | bull |
| CZ6.4 | BTC | 2025-H2 | misto |
| CZ6.5 | ETH | 2025-H2 | misto |
| CZ6.6 | SOL | 2025-H2 | misto |

1h timeframe pra sample bom + comparável a CY direto.

## Gate pré-registrado

Mesmos tresholds CY:
- **Candidato manifest**: ≥3/6 Sh ≥ 1.0 + trades ≥ 30 → abrir v-macrossover manifest
- **Staging exploration**: ≥2/6 Sh ≥ 0.5 → registro com flag
- **Refutação**: <2/6 Sh ≥ 0.5 → família trend-following 1h fechada (junto com Donchian)

Diferença esperada vs Donchian: MACX é lag-follower mais suave (não pega fake-outs de topo/fundo como Donchian). Hipótese intuitiva: menos ruim em bull (CY.1-CY.3), mas ainda perdedor em misto (CY.4-CY.6).

Timebox: ~6min wall. Closeout em ADR-0125.
