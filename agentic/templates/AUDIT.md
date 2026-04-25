# AUDIT.md — {{NOME DA ESTRATÉGIA}}

> **Template.** Copie para `agentic/active/<slug>/AUDIT.md` e preencha. Remova este bloco de nota ao finalizar.
> Produzido pelo `risk-auditor` após `VALIDATION.md` + `BACKTEST.md`.
> Assinatura humana é **obrigatória** para qualquer promoção (vision/02-scope + CLAUDE.md §3).

---

## Resumo executivo

{{3 linhas honestas. "Piloto reprovou porque X", "piloto tem edge marginal condicional a Y", etc.}}

## Blockers

Coisas que **reprovam** o piloto hoje. Cada item deve ser factual e ter caminho de remediação.

1. {{Blocker #B-1 — descrição + evidência + remediação}}.
2. {{...}}

## Riscos operacionais

Coisas que podem dar ruim em paper/canary (se alguma vez existir paper). Não são blockers agora, mas devem ser resolvidos antes de promoção.

1. {{Risco #R-1 — descrição + mitigação candidata}}.

## Compliance do laboratório

Checklist item por item:

- [ ] `LIVE_TRADING=false` confirmado em código/config.
- [ ] Hard cap de alavancagem (≤10x) respeitado.
- [ ] Sizing é fixed fractional (ADR-0004); sem martingale/averaging/grid oculto.
- [ ] Nenhum `import ccxt`/`binance.client`/`.create_order` em `src/`.
- [ ] Secrets fora do repo (`.env`, chaves, credenciais).
- [ ] Paper/live **não** tratado como se existisse.
- [ ] Testes property-based de causalidade verdes, OHLCV completo.
- [ ] Monotonicidade de custo (ADR-0010 + ADR-0019) verde nos 3 eixos.
- [ ] `walk_forward.json`, `monte_carlo.json`, `cost_stress.json`, `run.json` persistidos (ADR-0015 + ADR-0017).

## Evidências consultadas

- **Arquivos lidos:** {{lista}}.
- **Testes rodados:** {{suíte N passed}}.
- **Comandos executados:** {{lista}}.
- **ADRs checadas:** {{lista}}.

## Release decision

**Decisão:** `{{fail | paper_only | canary_only}}`.

Critério vigente — **ADR-0025** (híbrido):

- **`canary_only`** — hard gate absoluto: `hit_rate ≥ 45%` no baseline. Sem exceção.
- **`paper_only`** — gate relativo: piloto entre os **top-3 por `composite_score`** (ADR-0024) em sample de **N ≥ 9** pilotos válidos. Sample menor: canal relativo indisponível.
- **`fail`** — caso contrário.

> **`live` nunca é opção.** Hook bloqueia, e esta decisão recusa por doutrina também (ADR-0005).
> Hoje (2026-04): `paper_only` exige módulo `paper-trade` que não existe → decisão é formal; execução de paper depende de infraestrutura futura.
> Revisar decisão mais tarde? **Append** nova seção `## Re-auditoria YYYY-MM-DD (ADR-NNNN)` no fim deste arquivo. Nunca reescrever o histórico.

## Condicionais

"Este piloto vira `paper_only` se e somente se os itens abaixo forem resolvidos":

- {{condição 1}}
- {{condição 2}}

## Assinatura

- **Auditado por:** {{risk-auditor (agente) + usuário}}.
- **Data:** {{YYYY-MM-DD}}.
- **Confirmação humana:** {{obrigatória para paper_only/canary_only — requer commit explícito do usuário}}.
