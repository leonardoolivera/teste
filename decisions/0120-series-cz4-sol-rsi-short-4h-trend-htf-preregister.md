# 0120 — Série CZ4 pré-registro: SOL RSI short 4h + trend_htf(1d) cross-window

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0084 (v6 trend_htf rescue 1h), ADR-0119 (CZ2 staging), Padrão 26

## Motivação

CZ2 fechou staging contextual: 1 strict + 1 contextual + 1 FAIL bull-regime-oposto. Padrão 26 atribuiu o FAIL ao short sem filter direcional em bull. Hipótese: **trend_htf(1d, short_only)** filtra os bulls e eleva o agregado a 3/3 PASS, possivelmente strict cross-window — destrancando promoção v9-4h-filtered.

V6 (1h) usou trend_htf(4h, sma_20, short_only) para rescue. Em base 4h, equivalente natural é htf=1d (4h base × ~6 = 1d).

SOL 4h 2024-H1 não disponível (dataset missing) — 3ª janela permanece bloqueada por infra. CZ4 testa a alternativa "filter direcional" do critério de promoção do ADR-0119.

## Escopo

3 runs, RSI(14/30/70) short, SOL 4h, regime_filter trend_htf(1d, sma=20, short_only):

| Tag | Janela | Regime base | Hipótese |
|---|---|---|---|
| CZ4.1 | 2024-H2 | bull | filter ativa pouco → trades baixos, mas evita FAIL-em-bull |
| CZ4.2 | 2025-H1 | chop | filter ativa bastante → similar/melhor que CZ2.2 (Sh=0.64) |
| CZ4.3 | 2025-H2 | misto | filter mantém o melhor (baseline CT.3 Sh=2.81) |

## Gate pré-registrado

Naked baseline para comparação:
- CT.3 (2025-H2 naked): 23 trades, Sh=2.81
- CZ2.1 (2024-H2 naked): 13 trades, Sh=-1.31 FAIL
- CZ2.2 (2025-H1 naked): 17 trades, Sh=0.64

Gates filtered:
- **Promoção v9-4h-filtered**: 2/3 com Sh ≥ 1.0 + trades ≥ 8 (filter reduz n) + Sh_filtered ≥ Sh_naked em ≥2/3 → abrir manifest paralelo v9-4h-filtered
- **Salvamento contextual**: 3/3 Sh ≥ 0.3 (filter elimina FAIL bull) → adiciona evidence ao staging CZ2 mas não promove
- **Refutação**: filter degrada baseline (CZ4.3 Sh < 1.5) sem ganhar nada nas outras → trend_htf(1d) não é o filter certo em 4h

Trades≥8 relaxado por sample-constraint (Padrão 30) + filter cut.

Timebox: ~5min wall. Closeout em ADR-0121.
