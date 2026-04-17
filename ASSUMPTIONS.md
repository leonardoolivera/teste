# ASSUMPTIONS.md

> Suposições tomadas ao instalar a **camada agentic** sobre o Alpha Forge, quando o pedido do usuário era ambíguo ou colidia com estrutura existente. Cada item é ativo até o usuário refutar.

---

## A1 — Overlay, não substituição

O Alpha Forge já segue o protocolo `agent-project-template` (AGENTS.md, STATE.md, vision/, system/, decisions/). A camada agentic (SPEC/IMPLEMENTATION/VALIDATION/BACKTEST/AUDIT/CHECKLIST + subagentes + hooks) foi instalada **como overlay**: convive com a estrutura existente, não a substitui.

- `AGENTS.md` continua sendo a fonte de verdade do protocolo geral.
- `STATE.md` raiz continua sendo o estado vivo do projeto.
- `decisions/` continua sendo o registro imutável de decisões.
- Os artefatos novos são **específicos por hipótese de estratégia** — cada piloto nasce com seu próprio SPEC/IMPLEMENTATION/VALIDATION/BACKTEST/AUDIT, não substituem os documentos globais.

## A2 — CLAUDE.md estendido, não reescrito

`CLAUDE.md` original apontava somente para `AGENTS.md`. Foi **estendido** — preservando o ponteiro e adicionando as seções pedidas (objetivo, segurança, proibição de live trading, secrets, promoção, source-of-truth). Reescrever do zero contrariaria a regra `"AGENTS.md é fonte de verdade do protocolo"`.

## A3 — Piloto mínimo é Donchian breakout (ADR-0011)

O pedido foi "escolher UMA estratégia de referência simples e auditável". O projeto **já tem ADR-0011 aprovada** (Donchian breakout long-only) aguardando implementação. Criar uma estratégia paralela só para o piloto agentic violaria o protocolo ADR-first. Então:

- Implementação do piloto = implementação da ADR-0011.
- SPEC.md do piloto = projeção operacional da ADR-0011 no contrato agentic.
- Nada de MA crossover/RSI/exótica — Donchian é a hipótese definida.

## A4 — Live trading fica travado por hook, não só por doutrina

Além de documentar "proibido live trading", foi instalado um hook `PreToolUse` (`.claude/hooks/block_live_trading.py`) que bloqueia:

- `LIVE_TRADING=true` em qualquer comando.
- edição de `.env`, `.env.*`, `secrets*`, `*.pem`, `*.key`, `credentials*`.
- imports / invocações de `ccxt`, `binance.client`, `exchange.create_order`, `.execute()` em contexto de ordem real.
- URLs de endpoints reais de trading (`api.binance.com`, `fapi.binance.com`, `api.bybit.com`, etc.) em configs.

**Suposição:** o hook bloqueia por prefixos e regex simples. Se o usuário tiver necessidade legítima de acesso (ex: ingestão histórica via URL pública `data.binance.vision`), essa URL já está na lista de exceções. Qualquer falso positivo que travar o fluxo deve ser tratado abrindo ADR, não desligando o hook.

## A5 — Stages de release e default do piloto

Defaults do piloto:

- `LIVE_TRADING=false` (sempre).
- `release_mode=backtest_only` (sempre, inicial).
- **Nunca há promoção automática.** Promoção para `paper_only` exige: `AUDIT.md` com `release_decision: paper_only`, commit da evidência (`BACKTEST.md`, `VALIDATION.md`), revisão humana.
- **`live_trading` nunca é um release_mode válido no piloto.** Se algum dia existir, nasce em repositório separado.

## A6 — Source of truth

Artefatos + git são a única fonte de verdade. Nada de "o chat acordou que...". Toda decisão vira ADR; todo estado vive em `STATE.md` ou no artefato agentic correspondente; nada sobrevive só na memória implícita da sessão.

## A7 — Stack Python preservada

`uv`, `ruff`, `pyright`, `pytest`, `hypothesis`, `vectorbt` ficam. Os subagentes e hooks **não** introduzem dependências novas — tudo que foi adicionado roda com a stdlib ou com o que já está em `pyproject.toml`. Hooks são scripts Python stdlib puros para serem portáveis em Windows/WSL2/Linux.

## A8 — Subagentes Claude Code são overlay sobre o agente principal

Os cinco subagentes (`lead-orchestrator`, `strategy-researcher`, `strategy-implementer`, `backtest-validator`, `risk-auditor`) vivem em `.claude/agents/`. Eles **não** executam código automaticamente — são chamados sob demanda. O contrato é: quando o usuário (ou o lead-orchestrator) invoca um subagente, ele segue o protocolo do AGENTS.md **+** o contrato do artefato agentic que deve produzir.

## A9 — CI: adicionar um workflow agentic sem quebrar o existente

`ci.yml` já roda ruff + ruff format + pyright + pytest. Foi adicionado `.github/workflows/agentic.yml` que roda:

- smoke test do backtest.
- validação de artefatos (presença de SPEC/IMPLEMENTATION/VALIDATION/BACKTEST/AUDIT/CHECKLIST quando há piloto ativo).
- `scripts/validate_pilot.py` para checar coerência (commit ↔ SPEC ↔ VALIDATION ↔ AUDIT).

O workflow agentic **não bloqueia** CI principal — falha nele produz warning, mas não reprova PR (até que seja explicitamente ligado pelo usuário).

## A10 — Observabilidade de backtest fica para depois

Uma das frentes candidatas em STATE.md era observabilidade (logging estruturado de fills). Não foi tocada aqui — o piloto agentic é ortogonal, não compete. Quando o usuário quiser ligar, abre ADR específica.

## A11 — Paper-trade continua deferred

Explicitamente declarado em `vision/02-scope.md` como deferred. O pedido pediu que `README_AGENTIC_PILOT.md` explique "como promover de backtest_only para paper_only" — a resposta é: **não pode ainda**, porque o módulo `paper-trade` não existe. O README documenta isso sem inventar caminho.

## A12 — Nenhuma pergunta ao usuário

O usuário foi explícito: "não me faça perguntas; faça suposições razoáveis e siga". Todas as ambiguidades viraram item aqui em vez de virar pergunta.
