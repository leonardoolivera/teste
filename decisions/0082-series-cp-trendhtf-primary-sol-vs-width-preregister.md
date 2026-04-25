# 0082 — Série CP: TrendHTF como filter primário SOL (vs v4a width) — pré-registro

**Status:** Accepted — pré-registro; execução autorizada
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0079 (CO closeout — Padrão 17, nota a v4a), ADR-0075 (CK closeout — Padrão 15), ADR-0069 (v4a/v4b ativos)

## Contexto

CO audit (ADR-0079) revelou que em SOL 2025-H1, **trend-only Sh=1.96 > v4a width-only Sh=1.32**. Width em v4a funciona como "filtro de ruído" — passa gate, mas não é alinhado à direção do edge. Trend-only seria alternativa semanticamente melhor (Padrão 13: filter alinhado ao payoff direcional).

Pergunta aberta: **trend-only mono-SOL generaliza cross-period como v4a generaliza?** Precisa audit direto com mesmas 3 janelas que v4a/v4b cobrem SOL (2024-H2, 2025-H1, 2025-H2) + Gate B load-bearing em cada PASS.

## Decisão

Série CP mono-SOL, 3 pilotos cross-period, RSI(14/30/70) short + TrendHTF(4h, sma=50, short_only) como **filter primário** (não composto).

### Matriz (3 pilotos SOL)

- CP.1 — SOL 2024-H2
- CP.2 — SOL 2025-H1
- CP.3 — SOL 2025-H2

**Referências já arquivadas (reusam runs existentes):**
- CK.1 SOL 2024-H2 trend-only Sh=−1.02 (FAIL)
- CO.2-audit-noWidth SOL 2025-H1 trend-only Sh=1.96 (PASS)
- CO.3-audit-noWidth SOL 2025-H2 trend-only Sh=2.71 (PASS)

**CP = re-leitura sistematizada dos 3 com gates pré-registrados + Gate B comparativo vs v4a/v4b.** Não gera novos runs — aplica framework de decisão a runs existentes.

### Parâmetros de engine (já executados)

- capital 10000, fracao 0.1, alavancagem 2.0, fixed_notional
- taker 5bps, slippage 2bps, spread 0
- strategy rsi, period=14, oversold=30, overbought=70, no-long-only
- filter `trend_htf:htf=4h:sma_window=50:mode=short_only`
- n-folds 5, rolling, mc 1000, stress 2 cenários

### Gates pré-registrados

- **Gate 1 — principal:** ≥ **2/3** PASS critério manifest
- **Gate 2 — competir com v4a/v4b incumbentes:** em cada PASS, Sh trend ≥ Sh v4 incumbente
  - CP.2 vs v4a SOL 2025-H1 (Sh=1.32 width): precisa trend ≥ 1.32
  - CP.3 vs v4b SOL 2025-H2 (Sh=2.30 puro): precisa trend ≥ 2.30
  - CP.1 vs sem-incumbente (2024-H2 SOL não passa nenhum v4): não aplica
- **Gate 3 — Gate B load-bearing trend-only:** para cada CP PASS, rodar/comparar **RSI puro sem filter** no mesmo dataset; trend é load-bearing sse sem ele combo cai para FAIL.
  - CP.2 RSI puro SOL 2025-H1: **se não rodado ainda, executar**
  - CP.3 RSI puro SOL 2025-H2 = v4b SOL (Sh=2.30, PASS) → trend **não load-bearing** já antecipado
- **Gate 4 — promotion rule:** se Gate 1+2+3 PASS em ≥2/3 → abrir ADR de promoção v6 SOL-trend (combos escopados onde trend bate incumbente + é load-bearing). Se Gate 3 FAIL mesmo com Gate 1+2 PASS → Padrão 15 bloqueia (lift sem load-bearing).

## Hipóteses explícitas

1. **H-trend-bate-width** (CP.2+CP.3 PASS, trend Sh ≥ incumbente, load-bearing em ≥1/2): abre v6 track. Provável sucessor parcial do v4a.
2. **H-trend-amp-não-load-bearing** (CP PASS mas Gate 3 FAIL — já antecipado pra CP.3): replica CK result. NÃO-promoção. Confirma Padrão 15 mais uma vez.
3. **H-trend-não-generaliza-2024H2** (CP.1 FAIL já arquivado): limitação conhecida — trend não salva janela 2024-H2 (bull mkt).

## Saída da série

- **H-trend-bate-width PASS:** emitir ADR de promoção v6 SOL-trend (1-2 combos). Bridge AF↔bot posta mudança de stack.
- **H-trend-amp-não-load-bearing:** closeout analítico, NÃO-promoção. Reforça Padrão 15 pela 3ª vez (CK, CO, CP).
- **Confirmação Padrão 14:** SOL 2025+ é trend-amp-consistente; trend-only é track válido para pesquisa mas não para promoção isolada sem Gate B.

## Tooling

- Nenhum run novo necessário se RSI-puro SOL 2025-H1 já existe (verificar antes).
- Caso falte, 1 run adicional: `cp-audit-rsi-pure-sol-20250105_20250704-short` (RSI puro sem filter, SOL 2025-H1).

## Timebox

~2min compute (1 run audit se necessário) + ADR-0083 closeout mesmo turno.

## Critério de sucesso desta ADR

1. Framework aplicado aos runs existentes (CK.1, CO.2-audit-noWidth, CO.3-audit-noWidth)
2. Gate B (RSI puro SOL 2025-H1) verificado/executado
3. ADR-0083 emitida com decisão
