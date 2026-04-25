# 0132 — Série CZ4b pré-registro: SOL RSI short 4h + trend_htf(1W,4) (Padrão 31 corolário)

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0121 (CZ4 trend_htf 1d falhou), Padrão 31

## Motivação

CZ4 mostrou que trend_htf(1d, sma=20) destrói edge SOL 4h por ratio HTF/LTF inadequado (Padrão 31). Hipótese corolário: htf=1W, sma=4 produz ratio temporal equivalente ao v6 (1h base + 4h HTF + sma=20 = ~13 dias) → 1W*4 = ~28 dias é mais parecido com escala macro v6.

Se 1W,4 preserva CT.3 strict (Sh ≥ 2.0) E rescue CZ2.1 bull → filter direcional viável em 4h, abre v9-4h-filtered.

## Escopo

3 runs SOL 4h RSI short + trend_htf(1W, sma=4, short_only):

| Tag | Janela | Naked baseline |
|---|---|---:|
| CZ4b.1 | 2024-H2 bull | -1.31 (CZ2.1) |
| CZ4b.2 | 2025-H1 chop | 0.64 (CZ2.2) |
| CZ4b.3 | 2025-H2 misto | 2.81 (CT.3) |

## Gate pré-registrado

- **Promoção v9-4h-1Wfiltered**: 2/3 Sh ≥ 1.0 + 0/3 piora vs naked → manifest paralelo
- **Salvamento staging**: 3/3 Sh ≥ 0.5 + bull rescuado (Sh > 0) → reforça CZ2 staging
- **Refutação corolário Padrão 31**: <2/3 Sh ≥ 0.3 ou destrói CT.3 (Sh ≤ 1.5) → ratio 1W,4 também não é o certo, fechar tentativas trend_htf em 4h

Timebox: ~3min. Closeout em ADR-0133.
