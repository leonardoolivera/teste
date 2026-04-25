# 03 — Architecture

> **Layer:** Target.
> **Purpose:** declare the technical shape of the project — stack, runtime, deployment target, non-functional constraints.
> **Agent rule:** every major technical choice here must also exist as an ADR in `decisions/`. This file is the summary; ADRs are the argument.

---

## Stack

| Layer | Choice | Reason (short) | ADR |
|---|---|---|---|
| Language (backend) | Python 3.12+ | Ecossistema quant maduro (pandas/numpy/scipy/vectorbt); produtividade de pesquisa alta. | ADR-0001 |
| Framework (backend) | N/A | Alpha Forge é biblioteca + CLI + notebooks; não há web framework. | — |
| Engine de backtest | vectorbt | Vetorizado sobre pandas/NumPy + Numba; feito para pesquisa quantitativa em massa, ideal para varrer estratégias/parâmetros/cenários — que é o objetivo central do laboratório. | ADR-0001 |
| Dados / tabular | pandas + numpy | Padrão de facto; vectorbt é construído em cima deste ecossistema — trocar cedo aumenta atrito sem benefício. | ADR-0001 |
| Estatística / simulação | scipy | Cobre Monte Carlo, bootstrap e testes estatísticos necessários ao pipeline de validação. | ADR-0001 |
| Validação de config / schemas | pydantic v2 | Validação forte em runtime para configs de estratégia, parâmetros e experimentos — crítico para reprodutibilidade. | ADR-0001 |
| Config de experimentos | YAML via pyyaml | Legível, aceita comentários, padrão em ML/quant. | ADR-0001 |
| Testes | pytest + hypothesis | pytest como padrão; hypothesis (property-based) é decisivo para caçar lookahead em estratégias. | ADR-0001 |
| Plotting / relatórios | matplotlib + plotly | matplotlib para relatórios estáticos; plotly para exploração interativa em notebooks. | ADR-0001 |
| Notebooks | Jupyter | Padrão de pesquisa; integra bem com plotly e o ecossistema Python. | ADR-0001 |
| Integração exchange (deferred) | ccxt | Abstrai N exchanges numa API; entra só na camada futura de paper/live. | ADR-0001 |
| Language (frontend) | N/A | Biblioteca + CLI + notebooks, sem frontend dedicado. | — |
| Framework (frontend) | N/A | idem acima. | — |
| Database | N/A no núcleo | Datasets e resultados em **Parquet local + pathlib**; DuckDB fica como camada opcional **futura** de consulta, não como storage principal inicial. | ADR-0001 |
| Cache / queue | N/A | Sem serviços assíncronos no núcleo. | — |
| Auth strategy | N/A | Ferramenta local single-user. | — |
| Deployment target | Local developer machine | Windows com WSL2 preferencialmente, ou Linux/macOS; execução por CLI + notebooks. Cloud/distribuído são explicitamente `deferred`. | ADR-0001 |
| Gerenciamento de dependências | uv + pyproject.toml | Lockfile reproduzível (`uv.lock`), fluxo moderno de `sync/run/lock`, muito mais rápido que poetry/pip-tools. | ADR-0001 |
| Lint + format | ruff | Unifica linter + formatter num binário rápido; substitui black+flake8+isort. | ADR-0001 |
| Type checking | pyright | Rápido, excelente inferência; mypy só se aparecer necessidade específica. | ADR-0001 |
| CI/CD | GitHub Actions (mínimo) | Pipeline mínimo desde cedo: lint + tests + typecheck. Expansão só conforme necessidade real. | ADR-0001 |

## Repository shape

High-level layout. Details of each folder live inside them.

```
alpha-forge/
├── AGENTS.md                      # protocolo do template
├── CLAUDE.md                      # ponteiro para AGENTS.md
├── README.md                      # overview + quick start
├── STATE.md                       # estado atual (único doc do "agora")
├── pyproject.toml                 # metadata + deps (uv)
├── uv.lock                        # lock determinístico
├── .gitignore
├── .python-version                # pinar 3.12
│
├── vision/                        # alvo
├── system/                        # realidade implementada (cresce com o código)
├── decisions/                     # ADRs imutáveis
├── playbooks/                     # guias how-to
│
├── src/
│   └── alpha_forge/               # pacote Python instalável (src-layout)
│       ├── __init__.py
│       ├── data/                  # módulo 1
│       ├── strategies/            # módulo 2
│       │   ├── base.py            # interface comum long/short
│       │   ├── families/          # subpasta por família (breakout, momentum, ...)
│       │   └── registry.py
│       ├── regimes/               # módulo 3
│       ├── risk/                  # módulo 4
│       ├── backtest/              # módulo 5
│       ├── validation/            # módulo 6
│       ├── ranking/               # módulo 7
│       │   ├── scoring/           # subárea: métricas + score multiobjetivo
│       │   └── reporting/         # subárea: relatórios + export
│       ├── cli/                   # entrypoints (desde o início, mesmo que minimalistas)
│       └── io/                    # helpers transversais: parquet, paths, logging
│
├── tests/
│   ├── unit/                      # espelho leve de src/alpha_forge
│   ├── integration/               # pipeline end-to-end
│   ├── property/                  # hypothesis (anti-lookahead etc.)
│   └── fixtures/                  # SOMENTE dados pequenos e determinísticos
│
├── configs/                       # YAMLs versionados, fora de src/
│   ├── strategies/
│   ├── experiments/               # walk-forward, grid, MC
│   ├── risk/                      # orçamentos de risco
│   └── regimes/
│
├── notebooks/                     # Jupyter — exploração, não é produção
│   ├── exploratory/
│   └── reports/
│
├── data/                          # IGNORADO pelo git (exceto .gitkeep e manifesto)
│   ├── raw/
│   ├── processed/
│   └── datasets.yaml              # manifesto versionado (este entra no git)
│
├── results/                       # IGNORADO pelo git
│   ├── runs/
│   ├── validation/
│   └── rankings/
│
├── scripts/                       # utilitários transitórios; fluxos recorrentes migram para cli/ ou módulos
│
└── .github/
    └── workflows/
        └── ci.yml                 # pipeline mínimo: lint + tests + typecheck
```

**Notas estruturais (registradas para não serem relitigadas):**

- **src-layout** (`src/alpha_forge/`) — padrão moderno, protege contra import acidental do código em desenvolvimento.
- **`strategies/families/`** — cada família vira subpasta; arquivos soltos ficam inviáveis a partir de ~5 famílias.
- **`configs/` fora de `src/`** — configs YAML editáveis sem tocar código, versionadas para reprodutibilidade.
- **`data/` e `results/` fora do git** — apenas o manifesto `datasets.yaml` é versionado; binários Parquet geram ruído e peso.
- **Nome do pacote:** `alpha_forge` (snake_case, import-friendly).
- **`cli/` desde o início** — mesmo que minimalista; evita refactor tardio quando o projeto crescer.
- **`tests/fixtures/`** — somente dados pequenos e determinísticos; datasets reais vivem em `data/` (ignorado).
- **`scripts/`** — utilitário **transitório**; fluxos recorrentes (download de dados, reprocessamento, execução de experimentos) devem migrar para `cli/` ou módulos internos assim que se estabilizarem.

## Non-functional requirements

Números, não adjetivos. Valores em itálico são calibrações empíricas com data — serão revistos quando houver mudança estrutural (ex: entrada de `vectorbt` como engine via ADR-0001, entrada de `validation/` via ADR-0003).

### Performance

- **Backtest isolado** (1 estratégia × 1 ativo × 1 timeframe × 180 dias 1h = 4320 barras, dev local padrão): **≈ 0.9 s** com o engine Python atual. _(Medido 2026-04-17 no host de referência Windows 11 + Python 3.13, com MA crossover e Donchian breakout sobre BTC/ETH/SOL — tempos convergem em ~0.82–0.92 s por run; throughput ~4800 barras/s limitado pelo loop causal do engine.)_
- **Pipeline end-to-end** (backtest + walk-forward + Monte Carlo + stress de custos, 1 estratégia × 1 ativo × 1 timeframe × 2 anos em dev local padrão): meta **< 10 min**. _(Calibração 2026-04-17: extrapolação linear do backtest isolado para 2 anos dá ~3.5 s; walk-forward com ~30 folds ~= ~105 s; Monte Carlo de 1000 resamples opera sobre curva de equity pós-fato, não re-executa backtest, ~10–20 s; stress de 5 pontos de custo ~18 s — total plausível < 3 min mesmo com o engine Python atual. Meta de 10 min fica folgada mesmo antes de vectorbt (ADR-0001). Calibração definitiva depende de ADR-0003 entregar `validation/` e o script do pipeline completo existir.)_
- **Grid search** (varredura de ≥ 1.000 combinações para uma estratégia, dev local padrão): meta **< 2 h**. _(Calibração 2026-04-17: 1000 backtests × ~0.9 s = ~15 min em sequencial single-thread, folga de 8× sobre a meta. Com paralelismo trivial (processos ou vectorbt batch), margem cresce proporcionalmente. Meta permanece plausível mesmo sem vectorbt.)_
- **Uso de memória:** uma execução padrão (1 estratégia × 1 ativo × 1 timeframe × 2 anos) deve caber em **≤ 8 GB de RAM** no baseline. Acima disso é degradação ou bloqueio — precisa justificativa ou otimização.

### Correção e reprodutibilidade

- **Reprodutibilidade:** **100%** dos resultados do ranking reproduzíveis a partir de `(config, commit, dataset manifest)`. Dois runs na mesma terna produzem o mesmo score — tolerância zero para scores, tolerância documentada para ties.
- **Determinismo estocástico:** qualquer componente aleatório (Monte Carlo, bootstrap, shuffle) **exige seed explícito** e o seed é **persistido no manifesto do run**. Run sem seed persistido não entra no ranking.
- **Anti-lookahead:** **0 falsos negativos** em testes property-based (hypothesis) contra corpus sintético de estratégias com lookahead deliberado. Violação de lookahead é bug crítico, não warning.
- **Integridade de dados:** ingestão de OHLCV detecta **100%** dos gaps > 1 candle e registra no manifesto. Dataset com gap não declarado **não entra em ranking**.

### Retenção e rastreabilidade de runs

- Cada run tem **ID único**, **manifesto mínimo** (config + commit + dataset id + seeds + timestamps) e **estrutura reprodutível** em `results/runs/<id>/`.
- Purge manual de runs antigos é aceitável no início, desde que o formato permita remover runs individuais **sem quebrar a rastreabilidade** dos runs preservados.

### Qualidade de código

- **ruff** sem erros — CI bloqueia merge.
- **pyright** sem erros em `src/alpha_forge/` — CI bloqueia merge.
- **Cobertura de testes:** **≥ 85%** em `risk/`, `backtest/` e `validation/` (módulos financeiramente críticos); demais módulos sem meta rígida inicial.

### Testes

- `pytest tests/unit` em **< 45 s**.
- `pytest tests/integration` em **< 10 min**.
- **Fixtures versionadas** em `tests/fixtures/` devem ser **pequenas, sintéticas e determinísticas**; limite prático **< 5 MB por fixture**, salvo exceção justificada.

### Observability

- **Logging estruturado** (INFO por default, DEBUG opcional) em todos os módulos.
- Cada run de backtest/validação gera **`results/runs/<id>/run.log`** reproduzível.

### Security

- **Chaves de exchange nunca no repo.** Quando `ccxt` entrar (deferred), chaves ficam em `.env` fora do git.
- `.gitignore` cobre: `data/`, `results/`, `.env`, cache do uv, notebooks com outputs pesados.

### Não aplicáveis

- **Availability:** N/A — ferramenta local, não serviço.
- **Accessibility:** N/A — CLI + notebooks, sem UI web.
- **Compliance:** N/A no núcleo — pesquisa pessoal. Se virar copy-trade ou SaaS muda, mas está em `out of scope`.

## Constraints from the environment

- **Ambiente primário de desenvolvimento:** WSL2 em Windows, ou Linux/macOS. Windows nativo pode funcionar em tarefas limitadas, mas **não é o ambiente principal suportado** para o núcleo do projeto.
- **Hardware baseline assumido:** CPU multicore moderno (8+ threads), 16 GB RAM, SSD. **Sem GPU** no núcleo (vectorbt é CPU-bound).
- **Internet:** necessária para download de dados históricos e CI; pipeline de backtest/validação roda **offline**.
- **Ambiente corporativo (constraint real):**
  - Preferir **`uv`** (não exige admin).
  - Evitar instalações globais.
  - Minimizar dependência de privilégios administrativos.
  - **Não depender de Docker** no núcleo inicial.
  - **Não exigir serviços locais permanentes** (daemons, servidores).

---

## Interview checklist

- Every stack row has a choice and a one-line reason, OR is marked N/A.
- At least one ADR exists in `decisions/` for each non-trivial choice.
- Non-functional requirements are stated as numbers or clear yes/no criteria, not adjectives.
- Environmental constraints are listed when they exist (e.g. "corporate Windows without admin rights").
