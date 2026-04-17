# CLAUDE.md

Este arquivo é carregado automaticamente pelo Claude Code no início de toda sessão.

**→ Leia [`AGENTS.md`](./AGENTS.md) antes de qualquer coisa.** `AGENTS.md` é a fonte de verdade do protocolo geral (ordem de leitura, três camadas vision/system/state, interview, commits). Este arquivo só adiciona o que é específico da camada agentic cripto.

---

## 1. Objetivo do laboratório

Alpha Forge é um laboratório de pesquisa/backtest/validação/ranking de estratégias cripto com alavancagem até 10x. O propósito é **refutar hipóteses ruins rápido** e promover só o que sobrevive à validação. Retorno alto é **hipótese exploratória**, nunca critério de promoção. Princípios completos em [`vision/01-product.md`](./vision/01-product.md).

## 2. Política de segurança (hard rules — hooks aplicam)

- **Live trading está desligado.** `LIVE_TRADING` nunca pode ser `true`. O hook `.claude/hooks/block_live_trading.py` bloqueia comandos que tentem.
- **Nenhum código envia ordens reais.** `ccxt`, `binance.client`, `exchange.create_order`, `.execute_order(...)` são bloqueados em qualquer módulo de `src/`. Ingestão pública (`data.binance.vision`) é permitida.
- **Secrets não vivem no repo.** `.env`, `.env.*`, `secrets*`, `*.pem`, `*.key`, `credentials*` são bloqueados para edição. `.gitignore` já cobre.
- **Endpoints de produção de trading são bloqueados em configs.** `api.binance.com`, `fapi.binance.com`, `api.bybit.com`, `api.okx.com`, etc. Só `data.binance.vision` (histórico público) é permitido.

Se um hook bloquear algo legítimo, a resposta correta é **abrir ADR** explicando o caso, não desligar o hook.

## 3. Política de promoção entre estágios

Um piloto começa em `backtest_only` e só avança com evidência formal:

```
backtest_only  ──(VALIDATION verde + BACKTEST robusto + AUDIT=paper_only)──►  paper_only
paper_only     ──────────── HOJE: IMPOSSÍVEL ────────────►  live_trading
```

- **Promoção nunca é automática.** Precisa commit de `AUDIT.md` com `release_decision: paper_only | canary_only` + assinatura humana explícita.
- **`live_trading` não é um estágio atingível neste repositório.** Paper/live entra em repo separado, depois do núcleo maduro (ver `vision/02-scope.md` — deferred).
- **Evidência < rigor.** Retorno bonito não promove. Robustness score + stress de custos + detecção de overfitting promove.

## 4. Source of truth

- **Artefatos + git são a única fonte de verdade.** Nada de "o chat acordou que...".
- Decisão → ADR imutável em `decisions/`.
- Estado → `STATE.md` raiz.
- Hipótese de estratégia → `SPEC.md` (+ IMPLEMENTATION/VALIDATION/BACKTEST/AUDIT).
- Suposições tomadas por ambiguidade → `ASSUMPTIONS.md`.
- Se faltar artefato: o Stop hook (`.claude/hooks/check_gates.py`) reclama e empurra o trabalho a continuar.

## 5. Convenções de código e teste

- Python 3.12+, `src/alpha_forge/` em src-layout.
- Dependências: `uv`. Lint/format: `ruff`. Type check: `pyright` (strict em `src/`). Testes: `pytest` + `hypothesis`.
- Testes: `tests/unit/`, `tests/integration/`, `tests/property/`, `tests/fixtures/`. Property-based é obrigatório para causalidade.
- Toda nova estratégia: validação cedo e ruidosa no `__init__` (`TypeError`/`ValueError`), stateless, long-only nesta fase.
- Toda nova feature: ADR antes, código depois. `AGENTS.md` §4.

## 6. Camada agentic (overlay)

Esta camada é sobreposta ao protocolo de `AGENTS.md`, **não substitui**:

- `.claude/agents/` — 5 subagentes: `lead-orchestrator`, `strategy-researcher`, `strategy-implementer`, `backtest-validator`, `risk-auditor`.
- `.claude/hooks/` — PreToolUse (bloqueio live), SessionStart (reinjetar lembretes), Stop (checar gates).
- Artefatos por hipótese: `SPEC.md`, `IMPLEMENTATION.md`, `VALIDATION.md`, `BACKTEST.md`, `AUDIT.md`, `CHECKLIST.md`.
- `STATE.md` raiz continua sendo o diário do projeto; artefatos agentic são o registro de uma **hipótese específica** em andamento.

Para entender os contratos de cada artefato: ver [`README_AGENTIC_PILOT.md`](./README_AGENTIC_PILOT.md).
