# 0126 — Série CZ7 pré-registro: MACX 20/50 long + trend_htf filter (Padrão 33 teste)

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0125 (CZ6 MACX bull-only), Padrão 33

## Motivação

CZ6 mostrou MACX 20/50 long 3/3 strict em bull 2024-H2 mas 3/3 FAIL em misto 2025-H2. Padrão 33 exige filter antes de promoção. Hipótese: trend_htf(4h, sma=50, long_only) — mesma receita canônica v6 que resgatou RSI short — evita trades em regimes não-tendenciais e preserva edge bull sem destruir em misto.

## Escopo

6 runs, MA Crossover 20/50 long 1h + trend_htf(4h, sma=50, long_only), mesma matriz CZ6:

| Tag | Asset | Janela | Naked baseline (CZ6) |
|---|---|---|---:|
| CZ7.1 | BTC | 2024-H2 bull | Sh=2.39 |
| CZ7.2 | ETH | 2024-H2 bull | Sh=1.88 |
| CZ7.3 | SOL | 2024-H2 bull | Sh=1.22 |
| CZ7.4 | BTC | 2025-H2 misto | Sh=-2.17 |
| CZ7.5 | ETH | 2025-H2 misto | Sh=-1.47 |
| CZ7.6 | SOL | 2025-H2 misto | Sh=-2.44 |

## Gate pré-registrado

- **Promoção manifest v-macrossover-filtered**: ≥4/6 Sh≥1.0 + trades≥20 + Sh_filtered ≥ Sh_naked ou ≥0 em ≥5/6 → abrir manifest real + ADR promoção
- **Salvamento staging**: filter evita FAIL (≤1/6 Sh<0) + mantém ≥3/6 Sh≥1.0 em bull → staging reforçado, pendente cross-window
- **Refutação**: filter degrada bull <2/6 Sh≥1.0 → trend_htf(4h,50) não é o filter certo pra MACX 1h

Bar mais alta que CZ6 (4/6 vs 3/6) porque filter precisa provar valor, não só replicar.

Timebox: ~6min wall. Closeout em ADR-0127.
