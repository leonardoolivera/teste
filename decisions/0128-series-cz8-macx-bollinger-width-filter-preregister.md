# 0128 — Série CZ8 pré-registro: MACX 20/50 long + bollinger_width filter (Padrão 34 corolário)

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0127 (CZ7 trend_htf falhou), Padrão 34

## Motivação

CZ7 mostrou que trend_htf(4h,50) destrói edge MACX por lag composto (Padrão 34). Hipótese de salvamento: **bollinger_width(30,1.5,min_300bps)** é filter sem lag adicional — só checa vol da janela atual, não SMA HTF longa. Filter ativa quando há expansão de vol (= tendência em formação) e desativa em squeeze (= chop).

Se MACX + bollinger_width preserva bull e neutraliza misto → MACX vira candidato real (apenas 1 etapa do Padrão 34 corolário). Se também falha → engine MACX 20/50 inviável independente de filter.

## Escopo

6 runs, MACX 20/50 long 1h + bollinger_width(30,1.5,min_width_bps=300), mesma matriz CZ6/CZ7:

| Tag | Asset | Janela | Naked CZ6 | Trend_htf CZ7 |
|---|---|---|---:|---:|
| CZ8.1 | BTC | 2024-H2 | 2.39 | 1.61 |
| CZ8.2 | ETH | 2024-H2 | 1.88 | -0.06 |
| CZ8.3 | SOL | 2024-H2 | 1.22 | 0.24 |
| CZ8.4 | BTC | 2025-H2 | -2.17 | -2.89 |
| CZ8.5 | ETH | 2025-H2 | -1.47 | -0.26 |
| CZ8.6 | SOL | 2025-H2 | -2.44 | -1.60 |

## Gate pré-registrado

- **Promoção manifest v-macrossover-bw**: ≥4/6 Sh≥1.0 + trades≥15 + filter melhora vs naked em ≥4/6 → abrir manifest real
- **Salvamento staging**: ≥3/6 Sh≥1.0 (preserva 3 bull) + ≤1/6 Sh<-1 (mata FAIL profundo) → staging com flag, próxima etapa cross-window
- **Refutação final MACX**: <2/6 Sh≥0.5 → MACX 20/50 inviável independente de filter, família trend-following encerrada por enquanto

Bar de promoção alta (4/6) — filter precisa salvar bull E mitigar misto pra valer.

Timebox: ~6min wall. Closeout em ADR-0129.
