# CHECKLIST.md — Piloto {{NOME DA ESTRATÉGIA}} (backtest_only)

> **Template.** Copie para `agentic/active/<slug>/CHECKLIST.md` e preencha os gates conforme avança.
> Gate ativo: **{{gate atual — ex: `pesquisa`}}**.

---

## Gates (ordem fixa, nunca pular)

### 1. Pesquisa — produzido por `strategy-researcher`

- [ ] `SPEC.md` em `agentic/active/<slug>/` com todas as 13 seções preenchidas.
- [ ] ADR de estratégia (se aplicável) em `decisions/` com status `Proposed` ou `Accepted`.
- [ ] Critério de refutação explícito e auditável.

### 2. Implementação — produzido por `strategy-implementer`

- [ ] Código em `src/alpha_forge/strategies/families/{{familia}}/` seguindo ADRs 0002 (causalidade) + 0006+0019 (custos) + 0008/0011 (padrão de estratégia).
- [ ] Testes unit em `tests/unit/test_{{familia}}.py` cobrindo validação, warm-up, entrada, saída, stateless, long-only (ou direção equivalente).
- [ ] Testes property em `tests/property/test_{{familia}}_causal.py` com OHLCV completo.
- [ ] `IMPLEMENTATION.md` em `agentic/active/<slug>/` com mapeamento SPEC→código e gaps declarados.
- [ ] Suíte verde: `python -m pytest -q`.

### 3. Validação e backtest — produzido por `backtest-validator`

- [ ] `VALIDATION.md` em `agentic/active/<slug>/` com conformidade ao SPEC item por item.
- [ ] `BACKTEST.md` em `agentic/active/<slug>/` com dataset, métricas, sensibilidade fee/slip/spread, walk-forward, Monte Carlo.
- [ ] Artefatos persistidos em `results/validation/<slug>/`: `walk_forward.json`, `monte_carlo.json`, `cost_stress.json`, `run.json`.
- [ ] Property-based de monotonicidade (ADR-0010 + ADR-0019) verde nos 3 eixos de custo.
- [ ] Comando de reprodução documentado (ADR-0017 via `run.json`).

### 4. Auditoria — produzido por `risk-auditor`

- [ ] `AUDIT.md` em `agentic/active/<slug>/` com blockers, riscos operacionais, compliance, release_decision.
- [ ] Decisão ∈ `{fail, paper_only, canary_only}` — nunca `live`.
- [ ] Checklist de compliance item por item.
- [ ] Condicionais explícitas para promoção futura.

### 5. Release (não-automática)

- [ ] Commit de `AUDIT.md` com assinatura humana explícita.
- [ ] `STATE.md` raiz atualizado registrando a decisão.
- [ ] Se `release_decision = fail`: piloto encerra aqui; documenta o que foi aprendido em `STATE.md`.
- [ ] Se `release_decision = paper_only` ou `canary_only`: pré-requisito = existência do módulo `paper-trade` (hoje **não existe** — vision/02-scope deferred).

---

**Regras duras:**

1. Nunca avance de gate com gate anterior vermelho.
2. Nunca assuma que `live` é uma opção (ADR implícita em CLAUDE.md §3).
3. Cada gate é verificável sem ambiguidade — se está em dúvida, está vermelho.
4. Hook `check_gates.py` (Stop) cobra presença/coerência dos artefatos enquanto piloto está ativo em `agentic/active/<slug>/`.
