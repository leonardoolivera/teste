# 0085 — Série CR pré-registro: TrendHTF cross-asset BTC/ETH 2025-H1 (generalização v6)

**Status:** Accepted — pré-registro antes de rodar
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0084 (v6 ativado SOL 2025-H1), ADR-0083 (CP closeout + Padrão 19), ADR-0069 (v4a/v4b), Padrão 14 (filter direcional asset-específico), Padrão 19 (Gate B múltiplas baselines)

## Hipótese

TrendHTF short_only é load-bearing em SOL 2025-H1 chop (v6 active, Sh=1.958). **Generaliza para BTC e ETH no mesmo regime 2025-H1 chop?**

- **H-generaliza:** trend-only funciona cross-asset em chop → expandir v6 para 3 combos (BTC+ETH+SOL 2025-H1)
- **H-asset-específico:** trend-only é SOL-only (Padrão 14 confirmado) → v6 permanece 1 combo, não expandir

Incumbente para comparação:
- **BTC 2025-H1:** v4a width Sh=1.688 (ativo)
- **ETH 2025-H1:** não está em nenhum manifest — apenas baseline naked disponível

## Design

**Pilotos:**

| Tag | Symbol | TF | Window | Filter |
|---|---|---|---|---|
| CR.1 | BTCUSDT | 1h | 2025-01-05..2025-07-04 | trend_htf(htf=4h, sma_window=50, mode=short_only) |
| CR.2 | ETHUSDT | 1h | 2025-01-05..2025-07-04 | trend_htf(htf=4h, sma_window=50, mode=short_only) |

**Gate B runs (Padrão 19 — ambas baselines):**

| Tag | Symbol | Filter | Propósito |
|---|---|---|---|
| CR.1-naked | BTCUSDT | none | Gate B filter-vs-naked (load-bearing estrito) |
| CR.2-naked | ETHUSDT | none | Gate B filter-vs-naked |

Total: 4 runs (~10min).

**Engine:** RSI(14/30/70) short, `long_only=false`. Mesmos invariantes runtime ADR-0030 (faithful, fixed_notional=2000, entry/exit market at open next bar, stop=disabled).

**Custos:** baseline 0.14%, stress 0.34% (fee +10%). Seed MC=42.

## Gates pré-registrados

### Gate 1 — Passes isolados
`≥1/2` PASS (Sh≥1.0, trades≥30, MDD≤20%, MC p5>9500, cost_r≥0.95).

### Gate 2 — Lift sobre incumbente
- **BTC:** trend Sh > v4a width Sh=1.688
- **ETH:** sem incumbente — Gate 2 não aplicável (só Gate 1+3)

### Gate 3 — Load-bearing vs naked (Padrão 19)
Trend load-bearing quando naked **FAIL** (Sh<1.0 OU MC p5<9500 OU trades<30).

Se naked já PASS → trend não load-bearing → Padrão 15 bloqueia promoção.

### Gate 4 — Promoção
**Promove** combo a v6 (expansão) quando:
- Gate 1 PASS (combo válido)
- Gate 3 PASS (load-bearing vs naked)
- Gate 2 PASS onde aplicável (lift sobre incumbente)

**Bloqueia** se qualquer um falhar.

## Interpretação dos resultados possíveis

| Cenário | Verdict | Ação |
|---|---|---|
| CR.1+CR.2 ambos PASS Gate 3 | trend generaliza cross-asset chop | expande v6 para 3 combos (ADR-0086) |
| Apenas CR.1 PASS Gate 3 | trend generaliza BTC mas não ETH | expande v6 para 2 combos (SOL+BTC) |
| Apenas CR.2 PASS Gate 3 | trend generaliza ETH mas não BTC | expande v6 para 2 combos (SOL+ETH) |
| Nenhum PASS Gate 3 | trend é SOL-específico | Padrão 14 confirmado; v6 fica com 1 combo |
| CR.1/2 FAIL Gate 1 mas naked também FAIL | RSI short não funciona em BTC/ETH 2025-H1 | fora escopo v6; regime específico não suporta engine |

## Riscos antecipados

1. **BTC 2025-H1 com trend-only pode FAIL Gate 1** (trade count colapsa sem filter de regime amplo como width). Aceitável — informação válida.
2. **ETH naked pode PASS** (se RSI puro já edge em ETH 2025-H1) → trend não load-bearing → bloqueia promoção ETH mesmo se Sh alto. Correto por design (Padrão 15+19).
3. **v4a.BTC conflito:** se CR.1 promove, BTC 2025-H1 estará em v4a (width) E v6 (trend). Duas opções (decisão no closeout):
   - Coexistência (ambos filters ativos com notionais separados) — mais exposição
   - v6 substitui v4a.BTC se Sh v6 > v4a (analogamente ao que fizemos com SOL)

Decisão no closeout dependendo do Sh observado.

## Critério de sucesso desta ADR

1. Sweep CR executado e resultados arquivados em `results/validation/`
2. ADR-0086 closeout documenta verdict por gate
3. Se promoção: v6 manifest atualizado OU ADR-0087 separada
4. Se refutação: Padrão 14 reforçado
5. STATE.md atualizado com lição
