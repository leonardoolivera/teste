# 0101 — Série CZB pré-registro: Bollinger short + width em DOT/AVAX 2025-H2 (alternativa engine ao RSI)

**Status:** Accepted — pré-registro
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0100 (CZA closeout), ADR-0098 (CZ closeout), Padrão 22 (filter não cria edge)

## Hipótese

CZA (RSI short + width300) refutou DOT/AVAX 2025-H2 com delta Sh +0.4 insuficiente. **Alternativa:** trocar engine de mean-reversion — Bollinger short em vez de RSI short — com mesmo filter width(300).

Racional:
- Bollinger captura reversão via desvio-padrão de preço (2 std bands), RSI via momentum oscillator. Sinais diferentes.
- Em majors 2025-H1, bollinger_short_width (v3, CG) teve edge melhor que RSI naked:
  - SOL 2025-H1: Bollinger Sh=2.71 vs RSI Sh=0.61 (sem filter)
  - BTC 2025-H1: Bollinger Sh=1.24 vs RSI Sh=1.69 (com filter)
- Se Bollinger tem outra distribuição de captura, pode revelar edge onde RSI não revelou.

**Mas:** Padrão 22 é fresco — diz que se naked é fraco, filter não resgata. Antes de pular direto pra CZB com filter, vale o **naked Bollinger** primeiro como probe cheap.

## Design (2 pernas, 4 runs total)

### Perna A — Bollinger naked (probe Padrão 22)
| Tag | Symbol | Window | Engine |
|---|---|---|---|
| CZB.1 | DOT | 2025-H2 | Bollinger(20/1.5) short `long_only=false`, sem filter |
| CZB.2 | AVAX | 2025-H2 | idem |

Propósito: medir Bollinger naked Sh. Se ≥ 0.5 → perna B justificada. Se < 0.3 → Padrão 22 sinaliza FAIL esperado com filter, documenta e encerra.

### Perna B — Bollinger + width(300) (condicional)
Só dispara se pelo menos um ativo em Perna A tem Sh ≥ 0.5:
| Tag | Symbol | Window | Engine |
|---|---|---|---|
| CZB.3 | DOT | 2025-H2 | Bollinger short + width(30/1.5/300) |
| CZB.4 | AVAX | 2025-H2 | idem |

Parâmetros canônicos Bollinger: window=20, num_std=1.5 (mesmos do v3 short_width).
Runtime faithful ADR-0030.

## Gates pré-registrados

### Gate 1 — PASS isolado
Sh ≥ 1.0, trades ≥ 30, MDD ≤ 20%, MC p5 > 9500, cost_r ≥ 0.95, PnL > 3%.

### Gate 2 — Load-bearing (Padrão 12) — só perna B
Delta Sh(filter) − Sh(naked mesmo ativo) ≥ +0.5.

### Gate 3 — Gate vs Padrão 22
Se Perna A < 0.3 Sh nos dois: encerra sem rodar B (Padrão 22 confirmado cross-engine).
Se Perna A ≥ 0.5 pelo menos em um: dispara B.
Zona 0.3-0.5: decisão manual.

### Gate 4 — Comparação cross-engine CZA
Se Perna B PASS DOT ou AVAX:
- Comparar com CZA.1/CZA.2: se Bollinger+width >> RSI+width, engine Bollinger é asset-specific winner.
- Se similares, sinal de ruído residual (não edge real).

## Riscos antecipados

1. **Padrão 22 prior forte**: DOT naked RSI 0.50, AVAX naked RSI -0.05. Se Bollinger naked similar ou pior, gate 3 dispara e abortamos.
2. **Bollinger e RSI podem ter alta correlação em 2025-H2 altcoins**: se ambos mean-revertem nos mesmos setups, substituir um pelo outro não resolve.
3. **Custo baixo**: 2 runs probe (~5min). Se refuta, sabemos que o problema é estrutural (asset) não engine-specific.

## Interpretação

| Perna A | Perna B | Verdict | Ação |
|---|---|---|---|
| 2/2 naked ≥ 0.5 | roda B | — | avalia B |
| 1/2 naked ≥ 0.5 | roda B só no ativo positivo? ou ambos? | — | rodar ambos (controle) |
| 0/2 naked ≥ 0.5 | não roda B | Padrão 22 confirmado cross-engine | encerra DOT/AVAX 2025-H2 definitivamente |
| B: 1+ PASS | — | novo manifest candidato | emite |
| B: 0/2 PASS | — | confirma DOT/AVAX refutados ambas engines e ambas configs | encerra |

## Critério de sucesso desta ADR

1. Perna A executada
2. Decisão sobre Perna B (rodar ou não) baseada em gate 3
3. Se B, executada
4. ADR-0102 closeout documenta verdict
5. STATE.md atualizado
