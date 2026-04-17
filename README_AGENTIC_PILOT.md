# README_AGENTIC_PILOT.md

> Resumo da camada agentic instalada sobre o **Alpha Forge**, junto com o piloto inicial (Donchian breakout long-only).
> **Estado do piloto:** `backtest_only`. **Release decision:** `fail` (ver [AUDIT.md](./AUDIT.md) §"release_decision").

---

## O que foi criado

### 1. Documentos de política e contrato

| Arquivo | Papel |
|---|---|
| [CLAUDE.md](./CLAUDE.md) | Estendido. Segurança, proibição de live, promoção, source-of-truth, convenções. Aponta para `AGENTS.md` como fonte do protocolo geral. |
| [ASSUMPTIONS.md](./ASSUMPTIONS.md) | Suposições tomadas para instalar o overlay sem quebrar o protocolo existente. |
| [SPEC.md](./SPEC.md) | Hipótese + contrato completo do piloto Donchian (mercado, timeframe, entradas, saídas, stops, sizing, fees, slippage, funding, condições inválidas, limitações). |
| [IMPLEMENTATION.md](./IMPLEMENTATION.md) | Arquivos alterados, mapeamento SPEC→código, decisões técnicas, gaps. |
| [VALIDATION.md](./VALIDATION.md) | Testes executados, conformidade por seção do SPEC, falhas conhecidas. |
| [BACKTEST.md](./BACKTEST.md) | Dataset, métricas, grid de sensibilidade fees × slippage, robustez, lookahead check. |
| [AUDIT.md](./AUDIT.md) | Revisão adversarial, blockers, riscos operacionais, compliance, release_decision. |
| [CHECKLIST.md](./CHECKLIST.md) | Gates: pesquisa, implementação, validação, auditoria, release. |

### 2. Subagentes (`.claude/agents/`)

| Agente | Modelo | Função |
|---|---|---|
| `lead-orchestrator` | sonnet, effort high | Conduz o fluxo ponta a ponta. Nunca avança sem gate verde. Só delega. |
| `strategy-researcher` | sonnet, effort high | Transforma hipótese em SPEC.md rigoroso. Modo plano. |
| `strategy-implementer` | sonnet, effort high | Traduz SPEC em código fiel. Atualiza IMPLEMENTATION.md. |
| `backtest-validator` | sonnet, effort xhigh | Roda testes + backtest + sensibilidade. Produz VALIDATION.md e BACKTEST.md. |
| `risk-auditor` | `claude-opus-4-7`, effort xhigh | Revisão adversarial. Produz AUDIT.md e decisão de release. |

### 3. Hooks determinísticos (`.claude/hooks/`)

- **`block_live_trading.py`** — PreToolUse. Bloqueia `LIVE_TRADING=true`, edição de `.env`/secrets/chaves, imports de venues reais em `src/`, URLs de endpoints de produção de trading. `data.binance.vision` (histórico público) é exceção explícita.
- **`session_reminder.py`** — SessionStart. Reinjeta as regras duras após compactação de contexto.
- **`check_gates.py`** — Stop. Verifica presença/coerência dos artefatos; força continuação se incompleto.

Registro em [`.claude/settings.json`](./.claude/settings.json), que também adiciona `permissions.deny` para comandos destrutivos e edição de secrets.

### 4. Código e testes do piloto

- `src/alpha_forge/strategies/families/donchian/strategy.py` — `DonchianBreakoutStrategy(entry_window, exit_window)`. Long-only, stateless, causal por construção (ignora `window.iloc[-1]`).
- `src/alpha_forge/cli/app.py` — `--strategy donchian --entry-window N --exit-window M`.
- `tests/unit/test_donchian_breakout.py` — 17 testes: validação, warm-up, entrada, saída, arbitragem EXIT>ENTER, ignora barra corrente, long-only, stateless.
- `tests/property/test_donchian_causal.py` — hypothesis com OHLC completo, 80 exemplos.

### 5. Scripts operacionais

- `scripts/validate_pilot.py` — grid de sensibilidade fees × slippage + sanidade de monotonicidade + artefato JSON em `results/validation/`.
- `scripts/validate_artifacts.py` — checa presença/coerência dos artefatos agentic; também usado no CI.

### 6. CI

- [`.github/workflows/ci.yml`](./.github/workflows/ci.yml) — **não foi tocado**. Lint + format + typecheck + pytest continuam bloqueando PR.
- [`.github/workflows/agentic.yml`](./.github/workflows/agentic.yml) — novo. `continue-on-error: true` (não bloqueia merge). Roda: validação de artefatos, smoke backtest, grid de sensibilidade sobre sintético.

---

## Como rodar

### Ambiente

Já está coberto por [playbooks/setup.md](./playbooks/setup.md):

```bash
uv sync --extra dev
```

(ou `pip install --user -e '.[dev]'` em Windows sem `uv`).

### Suíte completa

```bash
python -m pytest -q
# esperado: 86 passed, 1 skipped
```

### Backtest do piloto

```bash
# sintético (sanidade rápida)
python -c "from alpha_forge.cli.app import run; raise SystemExit(run(['run-demo', '--strategy', 'donchian', '--entry-window', '20', '--exit-window', '10']))"

# dataset real BTCUSDT 1h 180d (requer ingestão prévia)
python scripts/ingest_binance_vision.py --symbols BTCUSDT --timeframe 1h --start 2025-07-05 --end 2025-12-31
python -c "from alpha_forge.cli.app import run; raise SystemExit(run(['run-demo', '--strategy', 'donchian', '--dataset-id', 'btcusdt_1h_20250705_20251231_binance_spot', '--entry-window', '20', '--exit-window', '10']))"
```

### Grid de sensibilidade (fees × slippage)

```bash
python scripts/validate_pilot.py --strategy donchian \
    --dataset-id btcusdt_1h_20250705_20251231_binance_spot \
    --entry-window 20 --exit-window 10
```

Output impresso + artefato JSON em `results/validation/<timestamp>_donchian.json`.

### Verificação de artefatos

```bash
python scripts/validate_artifacts.py
# esperado: [validate_artifacts] OK — todos os artefatos presentes.
```

### Invocação dos subagentes (dentro do Claude Code)

No Claude Code, os subagentes são chamados automaticamente quando o lead-orchestrator decide delegar. Invocação manual via `Agent` tool no CLI:

- `Agent(subagent_type="strategy-researcher", ...)` — quando faltar SPEC.
- `Agent(subagent_type="strategy-implementer", ...)` — quando SPEC estiver pronta.
- `Agent(subagent_type="backtest-validator", ...)` — após implementação.
- `Agent(subagent_type="risk-auditor", ...)` — após validação/backtest.
- `Agent(subagent_type="lead-orchestrator", ...)` — para conduzir todo o fluxo.

---

## Limitações

1. **Não há `live_trading`.** Nem como opção. CLAUDE.md §3 é explícito; hook bloqueia qualquer tentativa.
2. **Não há `paper-trade` funcional.** É **deferred** em `vision/02-scope.md`. Não é bug do piloto; é escolha estrutural do produto.
3. **Piloto Donchian reprovou.** `release_decision = fail` — porque validação completa (walk-forward, Monte Carlo, grid de parâmetros, multi-asset) não foi rodada **e** porque a infra paper não existe. A estrutura do piloto é sólida; o veredito é sobre o estado do sistema, não sobre a família Donchian.
4. **`system/domain.md|api.md|flows.md` não refletem Donchian ainda.** Gap explícito (blocker #B-6 em AUDIT). Separação deliberada entre "overlay agentic" e "atualização da realidade".
5. **Hook de check_gates é informativo, não punitivo.** Pode ser ignorado pelo usuário se ele pressionar "parar" novamente na mesma sessão — é defesa contra esquecimento, não policial.
6. **CI agentic é `continue-on-error`.** Por design: não queremos bloquear PR em torno da camada agentic até o usuário ligar explicitamente.

---

## Próximos passos (para eventualmente destravar promoção)

Cada item mapeia para um blocker do [AUDIT.md](./AUDIT.md).

1. **Escrever property-based de monotonicidade de custo para Donchian** (blocker #B-2). Mecânico, ADR-0010 aplicada a `DonchianBreakoutStrategy`.
2. **Rodar grid search de parâmetros `(entry, exit)` ∈ {(10,5), (20,10), (30,15), (50,20)}** sobre o dataset real (blocker #B-3).
3. **Caracterizar em multi-asset** (ingerir ETHUSDT e SOLUSDT 1h 180d, rodar o mesmo grid) — blocker #B-4 parcial.
4. **Rodar walk-forward** mínimo 3 janelas (blocker #B-4 principal).
5. **Rodar Monte Carlo / bootstrap de trades** com seed persistida (blocker #B-5).
6. **Atualizar `system/domain.md|api.md|flows.md`** para refletir Donchian + camada agentic (blocker #B-6).
7. **Implementar equity guard + daily-loss limit** em código (risco operacional R-2).

---

## Como promover de `backtest_only` para `paper_only`

**Hoje: impossível.** Não existe caminho executável, por decisão de produto (`vision/02-scope.md` deferred). O que teria que acontecer:

1. Abrir **ADR própria** para o módulo `paper-trade` (escopo mínimo, interface, contrato de simulação vs execução).
2. Implementar a camada. Deve usar **apenas** endpoints de mercado em modo de leitura **ou** o próprio simulador do Alpha Forge — nunca um `POST /order` real.
3. Resolver **todos** os blockers do AUDIT.md (B-1 até B-6, mais R-1 e R-2 se aplicável).
4. `risk-auditor` rodar nova auditoria sobre o piloto + infra paper → precisa decidir `paper_only`.
5. Assinatura humana explícita no commit de `AUDIT.md`.

**Nota firme:** mesmo com `paper_only` um dia ativo, **`live_trading` nunca sai deste repositório**. Live trading é outro produto, em outro repo, com outra camada de risco e compliance. Esta postura é deliberada e protegida por hook.

---

## Referências cruzadas

- Protocolo geral: [AGENTS.md](./AGENTS.md).
- Estado vivo do projeto: [STATE.md](./STATE.md).
- Princípios e alvo: [vision/01-product.md](./vision/01-product.md), [vision/02-scope.md](./vision/02-scope.md), [vision/03-architecture.md](./vision/03-architecture.md).
- ADRs relevantes: [ADR-0002](./decisions/0002-anti-lookahead-as-infrastructure.md), [ADR-0004](./decisions/0004-minimal-risk-policy.md), [ADR-0005](./decisions/0005-dataset-versioning-and-manifest.md), [ADR-0006](./decisions/0006-minimal-execution-cost-model.md), [ADR-0007](./decisions/0007-minimal-backtest-metrics.md), [ADR-0010](./decisions/0010-cost-monotonicity-property-test.md), [ADR-0011](./decisions/0011-donchian-breakout-strategy.md).
