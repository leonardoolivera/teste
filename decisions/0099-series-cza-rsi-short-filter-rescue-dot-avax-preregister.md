# 0099 — Série CZA pré-registro: RSI short + width filter rescue em DOT/AVAX 2025-H2

**Status:** Accepted — pré-registro
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0098 (CZ closeout), ADR-0036 (Padrão 12 filter load-bearing), ADR-0083 (Padrão 19 Gate B múltiplas baselines)

## Hipótese

CZ refutou RSI short naked para DOT (Sh=0.50) e AVAX (Sh=-0.05) em 2025-H2. Padrão 20 refinado como seletivo-por-ativo.

**Hipótese CZA:** filter `bollinger_width(30/1.5/300)` — mesmo filter que funcionou em v4a BTC 2025-H1 e v7 ETH 2024-H2 long — pode recuperar edge em DOT/AVAX 2025-H2.

Argumento teórico: DOT/AVAX FAIL naked pode ser chop-heavy → width filter mata setups em baixa volatilidade (quando RSI extremes tendem a ser ruído) e mantém em alta volatilidade (quando reversão mean-reverting é real).

## Design

### Parâmetros canônicos
- Engine: RSI(14/30/70) short, `long_only=false`
- Filter: `regime_filter = bollinger_width(window=30, num_std=1.5, min_width_bps=300)`
- Runtime faithful ADR-0030

### Pilotos (2 runs)
| Tag | Symbol | Window | Naked baseline (CZ) |
|---|---|---|---:|
| CZA.1 | DOTUSDT | 2025-H2 | Sh=0.498 |
| CZA.2 | AVAXUSDT | 2025-H2 | Sh=-0.054 |

Total: 2 runs (~5min).

## Gates pré-registrados

### Gate 1 — PASS isolado (standard)
Sh ≥ 1.0, trades ≥ 30, MDD ≤ 20%, MC p5 > 9500, cost_r ≥ 0.95, PnL > 3%.

### Gate 2 — Load-bearing (Padrão 12 + 19)
Filter só é promovido se **delta Sh ≥ +0.5 vs CZ naked baseline**:
- DOT: CZA.1 Sh − 0.498 ≥ +0.5 → Sh(CZA.1) ≥ 1.0 (mesmo que Gate 1, coincide)
- AVAX: CZA.2 Sh − (-0.054) ≥ +0.5 → Sh(CZA.2) ≥ 0.45 (menor que Gate 1, então Gate 1 domina)

Em ambos, Gate 1 é o binding. Se Gate 1 PASS, delta automaticamente ≥ +0.5.

### Gate 3 — Promoção
Se PASS, combo vai para manifest **novo** `rsi_short_width_altcoins_2025h2_<data>.json` (não estender v8 porque engine muda — v8 é naked, esse teria filter).

Se 1/2 PASS: manifest single-combo.
Se 2/2 PASS: manifest dual-combo.
Se 0/2 PASS: encerra filter rescue naked altcoins; documenta que DOT/AVAX 2025-H2 não tem edge extraível com essas 2 engines.

### Gate 4 — Trade count após filter
Filter width(300) tende a cortar ~40-60% dos trades. DOT naked = 86, AVAX naked = 95. Pós-filter esperado ~35-55. Gate ≥30 deve segurar mas apertado.

## Riscos antecipados

1. **Filter pode cortar demais** — se trade count cair <30, Gate 1 FAIL trivial.
2. **DOT/AVAX naked Sh baixo sugere ausência de edge, não excesso de ruído** — filter rescue falha se não há padrão para capturar.
3. **Base rate baixa**: em séries anteriores cross-asset com filter (CR BTC/ETH trend), 0/2 PASS. Filter rescue não é garantido.

## Interpretação

| Cenário | Verdict | Ação |
|---|---|---|
| 2/2 PASS | filter rescue universal 2025-H2 altcoins | novo manifest dual-combo |
| 1/2 PASS | seletivo | manifest single-combo |
| 0/2 PASS | altcoins não-majors 2025-H2 refutados ambas engines naked+filter | encerra DOT/AVAX, documenta limite cross-universo |

## Critério de sucesso desta ADR

1. Sweep CZA executado (2 runs)
2. ADR-0100 closeout documenta verdict
3. Se PASS: manifest novo
4. STATE.md atualizado
