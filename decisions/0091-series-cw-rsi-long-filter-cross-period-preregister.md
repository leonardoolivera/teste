# 0091 — Série CW pré-registro: RSI long + regime filter cross-period (análogo v2 Bollinger)

**Status:** Accepted — pré-registro
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0090 (CV closeout — long naked refutado), ADR-0088 (Padrão 20), v2 Bollinger long+width (precedente análogo)

## Hipótese

CU+CV refutaram RSI long naked cross-asset cross-period (0/9 combos). Mas **v2 Bollinger long+width funciona** (3 combos ativos: ETH 2024-H1, BTC 2024-H2, SOL 2024-H2). Hipótese: **long em crypto 1h exige regime filter** (não naked). Testar se RSI long + filter recupera edge.

Sub-hipóteses:
- **H1 (width):** RSI long + bollinger_width(30/1.5/300) — gate de volatilidade como v4a short. Chop reversível lateral-baixa-vol tende ser mais reversivo.
- **H2 (trend_htf long_only):** RSI long + trend_htf(4h,50,long_only) — simétrico a v6 short_only. Filter direcional alinhado ao payoff (Padrão 13).

Escopo: testar H1 primeiro (menos variantes, análogo mais direto a v2+v4a). Se H1 refutar, considerar H2.

## Design (apenas H1 nesta rodada)

**Pilotos:**

| Tag | Symbol | Window | Filter |
|---|---|---|---|
| CW.1 | BTCUSDT | 2024-H2 | bollinger_width(30/1.5/300) |
| CW.2 | ETHUSDT | 2024-H2 | bollinger_width(30/1.5/300) |
| CW.3 | SOLUSDT | 2024-H2 | bollinger_width(30/1.5/300) |
| CW.4 | BTCUSDT | 2025-H1 | bollinger_width(30/1.5/300) |
| CW.5 | ETHUSDT | 2025-H1 | bollinger_width(30/1.5/300) |
| CW.6 | SOLUSDT | 2025-H1 | bollinger_width(30/1.5/300) |
| CW.7 | BTCUSDT | 2025-H2 | bollinger_width(30/1.5/300) |
| CW.8 | ETHUSDT | 2025-H2 | bollinger_width(30/1.5/300) |
| CW.9 | SOLUSDT | 2025-H2 | bollinger_width(30/1.5/300) |

Engine: RSI(14/30/70) long_only=true. Runtime invariants ADR-0030.

Total: 9 runs (~22min).

## Gates pré-registrados

### Gate 1 — Passes isolados
Sh≥1.0, trades≥30, MDD≤20%, MC p5>9500, cost_r≥0.95, PnL>3%.

### Gate 2 — Load-bearing vs naked (Padrão 19)
Para cada CW PASS, comparar vs CU/CV naked correspondente. Filter load-bearing se CU/CV naked FAIL no mesmo combo (baseline já coletado):

| Combo | CU/CV naked Sh | Precisa CW > esse |
|---|---:|---|
| BTC 2024-H2 | CV.1 +0.886 | trivial (FAIL gate 1 mas próximo) |
| ETH 2024-H2 | CV.2 +0.651 | precisa lift |
| SOL 2024-H2 | CV.3 −0.103 | trivial |
| BTC 2025-H1 | CU.1 +0.829 | precisa lift |
| ETH 2025-H1 | CU.2 −0.535 | trivial |
| SOL 2025-H1 | CU.3 +0.074 | trivial |
| BTC 2025-H2 | CV.4 −2.343 | trivial |
| ETH 2025-H2 | CV.5 +0.669 | precisa lift |
| SOL 2025-H2 | CV.6 +0.401 | precisa lift |

Filter só é load-bearing se **naked FAIL E CW PASS**. Naked já FAIL em todos 9 casos, então qualquer CW PASS é load-bearing por Padrão 19.

### Gate 3 — Promoção v7 candidato
≥1 PASS → emitir v7 candidato `rsi_long_width.json`. Stack aceitaria combo long diversificante.

### Gate 4 — Comparação com v2 Bollinger long (benchmark)
v2 Bollinger long tem 3 combos ativos. Se CW tiver PASS em combos onde v2 não cobre → complemento. Se overlap → duplicação (Padrão 12 pede evitar).

v2 cobre: ETH 2024-H1, BTC 2024-H2, SOL 2024-H2. **Overlap esperado: BTC 2024-H2, SOL 2024-H2 (CW.1, CW.3).** Se CW.1 ou CW.3 PASS, considerar cuidado Padrão 12 (duplicação). v2 é Bollinger engine, CW é RSI — engines diferentes, não duplicação estrita.

## Riscos antecipados

1. **Width como filter não-direcional para long** — width 300 é "alta volatilidade" threshold, usado em short como gate de ruído. Para long, pode não filtrar o mesmo tipo de setup ruim. Se FAIL geral, validar H2 (trend_htf long_only).
2. **Trade count colapsa pós-filter** — RSI long já tem sample modesto (47-70 trades naked em 6 meses); filter pode cortar 30-50% (como CR mostrou). Gate ≥30 pode não passar.
3. **v2 overlap** — se CW.1/CW.3 PASS em BTC/SOL 2024-H2, stack fica com 2 engines × mesmo ativo × mesma janela long. Padrão 12 não bloqueia (engines diferentes), mas merecerá nota.

## Critério de sucesso desta ADR

1. Sweep CW executado e arquivado
2. ADR-0092 closeout documenta verdict
3. Se promoção: v7 manifest emitido + ADR-0093 separada
4. Se refutação H1: decidir abrir CW-H2 (trend_htf) ou encerrar long-side definitivamente
5. STATE.md atualizado
