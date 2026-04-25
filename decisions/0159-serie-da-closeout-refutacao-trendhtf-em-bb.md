# 0159 — Série DA closeout: trend_htf em BB short refutado, width filter superior

**Status:** Accepted — refutação screening. Canônicos BB short mantidos com width filter.
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0158 (pré-reg), Padrão 43

## Resultado

| Tag | Combo | Trades | Sharpe | Lift vs width | PnL% |
|---|---|---:|---:|---:|---:|
| DA.1 | BTC bol + trend_htf | 51 | 1.04 | **-1.29** | 2.45 |
| DA.2 | ETH bol + trend_htf | 67 | 1.46 | **-0.94** | 6.00 |
| DA.3 | SOL bol + trend_htf | 69 | 3.16 | **+0.45** | 16.58 |

Baselines (width filter canônico): BTC 2.33, ETH 2.40, SOL 2.71.

## Avaliação gate (ADR-0158)

- Upgrade convergente: ≥2/3 lift > +0.5 → DB
- Signal divergente: 1/3 lift > +0.5 → Padrão 41 bloqueia
- Refutação: 0/3 → descartar

**0/3 lift > +0.5** (SOL é +0.45, aquém). **Refutação.**

## Interpretação

### trend_htf filter é **mais seletivo mas menos eficaz em BB**

Trade counts: DA.1-3 = 51/67/69. Width baselines tinham 77/101/101 (SOL) trades. trend_htf corta ~30% dos trades — seleciona regime mais estrito (4h SMA50 short-only). Mas a qualidade dos trades remanescentes NÃO compensa:

- **BTC**: PnL% caiu de ~14% (width) para 2.45% (trendhtf). trend_htf em 1h BTC cortou muito signal útil.
- **ETH**: PnL similar (6% vs ~7%) mas Sharpe muito menor — mais volatilidade por trade.
- **SOL**: único que melhora PnL (16.58% vs ~14.47%). Sharpe também melhora marginalmente.

### Por que difere de RSI + trend_htf (que funcionou)?

RSI + trend_htf 25/75 em SOL 2025-H1 deu Sh=2.00 (vs baseline 30/70 Sh=0.89 naked = +1.1 lift). Filter trend_htf potencializa RSI porque RSI gera sinais em tendências (divergências persistentes) que width não captura.

BB é mean-reversion pura: bandas extremas implicam **reversão local**. trend_htf força "só short em downtrend 4h", mas BB em downtrend 4h gera shorts na banda alta que falham (preço continua descendo, não reverte). **BB + trend_htf tem conflito estrutural**: BB pede reversão, trend_htf pede continuação de tendência.

width filter funciona para BB porque simplesmente corta regime de baixa volatilidade (onde mean-reversion não tem range para trabalhar). Não briga com a direção.

### Padrão 43 nuançado (nota interpretativa)

Padrão 43 disse "filter diferente diversifica mais que engine". Verdadeiro empiricamente no stack (CZ16/17/19), mas **não implica que trocar filter sempre melhora**. Filters interagem com engine logic:
- RSI + trend_htf: engines concordam (momentum-ish persistência) → boost
- BB + trend_htf: engines discordam (reversão vs continuação) → degradação

**Nova heurística (informal, não-Padrão)**: antes de trocar filter de engine, checar se filter e engine **concordam direcionalmente**. trend_htf implica "tendência persiste"; serve engines que surfam tendência (RSI bounds), não reversão pura.

## Decisão

- Nenhuma edição manifest
- Bollinger short fica com width filter — canônico v4a preservado
- trend_htf filter **não** é compatível com BB como filtro de regime
- Padrão 43 continua válido como heurística; DA é exemplo de nuance (interação engine-filter)

## Ação executada

- ✅ ADR-0158 pré-reg
- ✅ 3 runs DA
- ✅ ADR-0159 closeout

## Não-alvo

- Não testar trend_htf em BB long (mesma incompatibilidade direcional esperada, mas espelhada)
- Não explorar outros filters exóticos em BB sem hipótese estrutural

## Próxima frente na fila

Frente 3: composição AND filters (width AND trend_htf) — diferente de DA porque mantém width (boost mean-reversion) e adiciona trend_htf como gate extra.
