# agentic/

Camada de orquestração de pesquisa automatizada de estratégias. Importada do fork `feature/agentic-pilot-donchian` via [ADR-0020](../decisions/0020-agentic-overlay-import.md).

Esta camada **não toca `src/alpha_forge/`**. É overlay de protocolo + agents + hooks. Fornece infra pra rodar hipóteses de estratégia ponta-a-ponta (pesquisa → implementação → validação → auditoria) de forma reprodutível, em escala.

## Layout

```
agentic/
├── README.md                   # este arquivo
├── templates/                  # modelos dos 6 artefatos (intocáveis)
│   ├── SPEC.md
│   ├── IMPLEMENTATION.md
│   ├── VALIDATION.md
│   ├── BACKTEST.md
│   ├── AUDIT.md
│   └── CHECKLIST.md
├── active/                     # pilotos em andamento (um sub-diretório por hipótese)
│   └── <slug>/                 # ex: donchian-btc-180d/
│       ├── SPEC.md
│       ├── IMPLEMENTATION.md
│       ├── VALIDATION.md
│       ├── BACKTEST.md
│       ├── AUDIT.md
│       └── CHECKLIST.md
└── inactive/                   # pilotos concluídos/arquivados (opcional, criado on-demand)
    └── <slug>/
```

## Componentes

### 1. Templates (`agentic/templates/`)

6 modelos em Markdown com `{{PLACEHOLDER}}` para preencher. Nunca editar diretamente — copiar pra `agentic/active/<slug>/` e editar a cópia.

### 2. Subagentes (`.claude/agents/`)

| Agente | Modelo | Função |
|---|---|---|
| `lead-orchestrator` | sonnet | Conduz o fluxo ponta a ponta. Nunca avança sem gate verde. Só delega. |
| `strategy-researcher` | sonnet | Transforma hipótese em `SPEC.md` rigoroso. Modo plano. |
| `strategy-implementer` | sonnet | Traduz `SPEC.md` em código fiel. Atualiza `IMPLEMENTATION.md`. |
| `backtest-validator` | sonnet | Roda testes + backtest + sensibilidade (3 eixos de custo ADR-0019). Produz `VALIDATION.md` e `BACKTEST.md`. |
| `risk-auditor` | `claude-opus-4-7` | Revisão adversarial. Produz `AUDIT.md` e decisão de release. |

### 3. Hooks (`.claude/hooks/`)

- **`block_live_trading.py`** — PreToolUse. Bloqueia `LIVE_TRADING=true`, edição de secrets, imports de venues reais em `src/`, endpoints de produção de trading. `data.binance.vision` é exceção permitida.
- **`session_reminder.py`** — SessionStart. Reinjeta regras duras após compactação.
- **`check_gates.py`** — Stop. **Modo opt-in**: só ativa se há piloto em `agentic/active/<slug>/`. Exige artefatos completos enquanto piloto está ativo.

Registro em [`.claude/settings.json`](../.claude/settings.json).

### 4. Validator script (`scripts/validate_artifacts.py`)

Mesma lógica do `check_gates.py`, rodada em CLI/CI. Exit 0 se não há piloto ativo; exit 1 se algum artefato de piloto ativo está incompleto.

## Fluxo de abertura de um piloto

```bash
# 1. escolher slug (kebab-case curto)
SLUG=donchian-btc-180d

# 2. criar diretório e copiar templates
mkdir -p agentic/active/$SLUG
cp agentic/templates/*.md agentic/active/$SLUG/

# 3. invocar o orquestrador (no Claude Code)
# O lead-orchestrator lê o CHECKLIST e delega ao strategy-researcher.

# 4. acompanhar via validate_artifacts
python scripts/validate_artifacts.py
# Esperado: reporta quais gates estão faltando.

# 5. ao final, atualizar STATE.md com a decisão (fail/paper_only/canary_only)
# e mover (opcional) para agentic/inactive/$SLUG/.
```

## Fluxo de execução por gate

```
agentic/active/<slug>/ criado (por humano ou orquestrador)
    ↓
strategy-researcher → SPEC.md  ────────────── [gate 1: pesquisa]
    ↓
strategy-implementer → src/... + IMPLEMENTATION.md ── [gate 2: implementação]
    ↓
backtest-validator → VALIDATION.md + BACKTEST.md + results/validation/<slug>/*.json ── [gate 3: validação]
    ↓
risk-auditor → AUDIT.md (release_decision ∈ {fail, paper_only, canary_only}) ── [gate 4: auditoria]
    ↓
STATE.md raiz atualizado com decisão ─────── [gate 5: release — requer assinatura humana]
```

## Regras duras

1. **`live_trading` nunca é uma opção.** Hook bloqueia, doutrina recusa, protocolo não o oferece como output.
2. **Nunca pule gate.** Ordem é fixa (pesquisa → implementação → validação → auditoria). Gate vermelho vira volta pro gate anterior.
3. **Nunca edite ADR.** Se decisão precisa mudar, nova ADR supersede a antiga.
4. **ADR antes, código depois.** Qualquer mudança estrutural passa por ADR (vision ou decisão de arquitetura).
5. **Source of truth = git + artefatos.** Artefatos agentic são persistentes e versionados, não ephemeral.

## Como executar hoje, na prática

- **Se quer abrir piloto agora:** copie templates pra `agentic/active/<slug>/` e invoque `lead-orchestrator` via Claude Code (`Agent(subagent_type="lead-orchestrator", ...)`).
- **Se está testando a infra:** rode `python scripts/validate_artifacts.py` — em repo limpo (sem piloto), imprime "nenhum piloto ativo — OK".
- **Se `check_gates.py` está reclamando:** provavelmente existe `agentic/active/<slug>/` sem artefatos completos; ou preenche, ou move pra `agentic/inactive/`, ou remove o diretório.

## Referências

- [ADR-0020](../decisions/0020-agentic-overlay-import.md) — decisão de importar esta camada.
- [AGENTS.md](../AGENTS.md) — protocolo geral do projeto.
- [CLAUDE.md](../CLAUDE.md) — políticas de segurança e promoção.
- [STATE.md](../STATE.md) — estado vivo.
- [decisions/](../decisions/) — histórico de ADRs 0001–0020.
