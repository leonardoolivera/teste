# 0114 — Série CT pré-registro: RSI short cross-timeframe 4h (CN' renomeado)

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** backlog item 2 (CN' 4h cross-timeframe)

## Motivação

Todo stack atual é 1h timeframe. Hipótese cross-timeframe: edges RSI short validados em 1h replicam em 4h? Se sim → diversificação de timeframe, menor trade count mas menor ruído, potencial stack paralelo 4h. Se não → edges 1h são timeframe-específicos.

## Escopo

3 runs, todos RSI short em 4h timeframe:

| Tag | Combo baseline (1h) | Engine 4h | Dataset |
|---|---|---|---|
| CT.1 | v4a BTC 2025-H1 short+width (Sh=1.69) | RSI short + width | btcusdt_4h_20250105_20250704 |
| CT.2 | v8.1 BTC 2025-H2 short naked (Sh=1.64) | RSI short naked | btcusdt_4h_20250705_20251231 |
| CT.3 | v8.1 SOL 2025-H2 short naked (Sh=2.30) | RSI short naked | solusdt_4h_20250705_20251231 |

Engine RSI(14/30/70) preservado — em 4h, RSI(14) cobre ~2.3 dias (vs 14h em 1h).

## Considerações técnicas

- **Trade sample menor** em 4h: esperado ~1/4 dos trades vs 1h (pela densidade de bars). Gate trades≥15 relaxado (vs 30 do stack ativo) porque cross-timeframe probe é exploratório.
- **MC p5** pode não atingir 9500 em sample pequeno. Uso alternativo: focar em Sh + PnL direction.
- **Filter width 300bps em 4h**: escala diferente (volatilidade 4h maior), mas computed on 4h bars — self-consistent.

## Gates pré-registrados

Por combo:
- **Replicação forte**: Sh ≥ 1.0 + trades ≥ 15 + PnL > 0
- **Replicação fraca (contextual-equivalent)**: Sh ≥ 0.5 + trades ≥ 10 + PnL > 0
- **Refutação**: Sh < 0 OU trades < 5 (subamostra extrema)
- **Ambiguo**: 0 ≤ Sh < 0.5

Agregado:
- 3/3 replicação forte → **promoção** a pre-register série 4h paralela (CT2 seria próxima)
- ≥2/3 replicação fraca → **open**: cross-timeframe mostra potencial, vale testar mais combos/janelas
- 0-1/3 PASS → **refutação**: edges RSI short são 1h-específicos, não escalar pra 4h

## Expectativa base

Probabilidade 50/50. Argumentos pro: RSI é indicador universal, não depende de micro-timeframe structure. Argumentos contra: trade count baixo em 4h pode matar edges estatisticamente; regime-shifts hit harder quando cada trade pesa mais.

Timebox: 3 runs ~5-8min wall. ADR-0115 closeout.
