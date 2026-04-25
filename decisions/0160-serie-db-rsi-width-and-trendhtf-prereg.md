# 0160 — Série DB pré-reg: RSI short + composição AND(width, trend_htf)

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário ("sim") + agente
**Relates to:** ADR-0159 (DA — trend_htf incompatível com BB), Padrão 17 (composição pernas), Padrão 43

## Hipótese

ADR-0159 refutou trend_htf ISOLADO em BB (conflito direcional). Mas em **RSI short** trend_htf SMA50 4h funciona (cz10/11 promoveu 25/75). Hipótese nova:

**AND(width, trend_htf) em RSI short** = intersecção dos dois regimes. Seleciona: (a) alta volatilidade (width > 300bps) AND (b) downtrend 4h (price < SMA50). Deveria ser **super-específico** — se cada filter isolado já dá Sh≈2, composição pode dar boost marginal OU degradar por corte excessivo de trades.

Escolha: usar RSI engine (concorda direcionalmente com trend_htf, diferente de BB).

## Padrão 17 check (pré-condição)

Padrão 17 exige que **ambas pernas da composição AND tenham FAIL isolado válido** antes de testar composição. Status:

| Perna | Isolado existe? | Refutado? |
|---|---|---|
| width isolado (RSI 30/70 BTC 2025-H1) | ✅ ch-rsi-14-30-70-btc-... Sh=1.69 | Não, é live combo |
| trend_htf isolado (RSI 30/70 BTC 2025-H1) | ❌ nunca testado isoladamente |

**Padrão 17 requer testar trend_htf ISOLADO em RSI 30/70 BTC antes de AND**. Incluir DB.0 como perna base.

## Probes (4 runs)

| Tag | Combo | Dataset | Filter |
|---|---|---|---|
| DB.0 | RSI 14/30/70 + trend_htf (baseline perna) | BTC 2025-H1 | `trend_htf:htf=4h:sma_window=50:mode=short_only` |
| DB.1 | RSI 14/30/70 + AND(width, trend_htf) | BTC 2025-H1 | `and(bollinger_width:window=30:num_std=1.5:min_width_bps=300,trend_htf:htf=4h:sma_window=50:mode=short_only)` |
| DB.2 | RSI 14/30/70 + AND(width, trend_htf) | ETH 2025-H1 | idem |
| DB.3 | RSI 14/30/70 + AND(width, trend_htf) | SOL 2025-H1 | idem |

Baselines (RSI 30/70 short + width canônico 2025-H1):
- BTC: Sh=1.69
- ETH: ~1.96 (estimado)
- SOL: ~2.02 (estimado)

## Gate pré-registrado

- **Upgrade convergente**: DB.1/2/3 lift > +0.5 em ≥2/3 E DB.0 Sh > 0.5 (trend_htf isolado é viável) → DC cross-era
- **Padrão 17 fail**: DB.0 Sh < 0.5 → trend_htf não tem edge isolado em RSI 30/70 BTC; AND inválido mesmo que funcione
- **Signal divergente**: 1/3 lift > +0.5 AND Padrão 17 passa → Padrão 41 bloqueia
- **Refutação**: 0/3 ou Padrão 17 fail → AND não funciona

## Não-alvo

- Não testar AND em BB (DA refutou trend_htf em BB)
- Não variar bounds RSI — canônico 30/70
- Não testar OR composição (escopo maior)

## Ação

- Script `tools/run_db_sweep.py`
- Closeout ADR-0161
