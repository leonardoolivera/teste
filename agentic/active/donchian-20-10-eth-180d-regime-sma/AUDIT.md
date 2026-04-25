# AUDIT.md — H.9 Donchian 20/10 ETH 180d + SMA

release_decision: fail

## release_decision

**`fail`** por critério 1 (`hit_rate=32.29% < 45%`) — **apesar de ser o piloto com melhor performance do protocolo**.

## Blockers

Nenhum. Pipeline limpo. Critérios 2, 3 e corroboração absoluta passam.

## Findings

1. **Asset é dimensão crítica.** ETH+SMA Pareto-domina BTC+SMA em fe (+14.23%), hit (+2.47pp), trades (−18) e mdd (−2.96pp). 11 pilotos anteriores BTC convergiram em faixa 25-30% hit; ETH com mesma estratégia+filtro pula para 32.29%.
2. **Primeiro fe > 10000 do protocolo.** 10504.18 — corroboração em termo absoluto passa pela primeira vez.
3. **Hit_rate ainda insuficiente.** Mesmo com asset "melhor", 32.29% continua a 12.71 pp abaixo do piso de 45%. Se o plateau BTC era ~30%, o plateau ETH parece ser ~32% — **deslocamento da faixa, não quebra do plateau**.
4. **ADR-0019 11ª confirmação.** Primeira com fe > 10000; invariante mantém.

## Recomendações

- **ETH é candidato natural para próxima série I** (dataset diferente, mesma família/pipeline) — ADR-0020 "gap mínimo primeiro" aplica; série H foi construída sobre BTC, série I iniciando com ETH pode mover hit mais alto.
- **Pesar se faz sentido continuar perseguindo hit ≥45%** — após 11 pilotos, nenhum cruzou o piso. Pode ser que o critério esteja calibrado para família de estratégia diferente; revisar baseline calibration (ADR D quando feita) com dados dos 12 pilotos.
- **Combinação ETH + filtros mais ricos (AND/OR composite, ATR)** não testada ainda — resevrar para série I.

---

## Re-auditoria 2026-04-18 (ADR-0025)

release_decision: paper_only

**Critério vigente:** híbrido (ADR-0025) — `canary_only` exige `hit_rate ≥ 45%` absoluto; `paper_only` exige top-3 por `composite_score` (ADR-0024) com N ≥ 9.

**Snapshot de ranking (2026-04-18, DEFAULT_WEIGHTS de ADR-0024):**

- Rank: **1/12**
- `composite_score`: **7.65**
- `hit_baseline`: **32.29%** (< piso de 45%)
- `fe_baseline`: **10504.18**
- `flags_digest`: `dfb4b002dfca168a`

**Justificativa:** top-3 por `composite_score` (ADR-0024) em sample N=12 ≥ 9 → canal relativo `paper_only` habilitado (ADR-0025).

**Decisão original preservada acima.** Esta seção é append imutável; revogações futuras devem ser **nova seção**, nunca edit.
