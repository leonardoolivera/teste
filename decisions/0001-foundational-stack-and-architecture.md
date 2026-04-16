# 0001 — Foundational stack and architecture for Alpha Forge

**Status:** Accepted
**Date:** 2026-04-16
**Deciders:** Usuário (operador/pesquisador) + agente (Claude Opus 4.7)

## Context

Alpha Forge é um laboratório de pesquisa, backtest rigoroso, validação estatística e ranking de estratégias de trading cripto com alavancagem até 10x. O produto precisa suportar varredura em massa de estratégias e parâmetros, validação anti-overfitting embutida (walk-forward, Monte Carlo, stress de custos), classificação por regime de mercado e ranking multiobjetivo — tudo rodando localmente, de forma reproduzível, em ambiente potencialmente corporativo (sem privilégios de admin, sem Docker no núcleo).

Antes de escrever qualquer linha de código, era preciso fixar: (i) as escolhas fundamentais de stack; (ii) a decomposição modular; (iii) as restrições de acoplamento entre módulos; (iv) as NFRs quantitativas que definem "pronto".

## Decision

Adotar **Python 3.12+ com vectorbt** como base do motor de pesquisa, decompor o sistema em **7 módulos** (`data`, `strategies`, `regimes`, `risk`, `backtest`, `validation`, `ranking`) com **acoplamento deliberadamente frouxo** (`strategies` não depende de `regimes`; `risk` não é mesclado em `backtest`), organizar o repositório em **src-layout** (`src/alpha_forge/`) com configs YAML fora do pacote e datasets/resultados fora do git, usando **uv + ruff + pyright + pytest+hypothesis + GitHub Actions** como toolchain.

## Consequences

### Positive

- **Produtividade de pesquisa alta:** vectorbt vetorizado em cima de pandas/numpy/Numba é desenhado para exatamente o caso de uso central do projeto — varredura em massa de estratégias/parâmetros/cenários. Casa com os diferenciais declarados em `vision/01-product.md` (validação embutida, stress de custos, classificação por regime, ranking multiobjetivo).
- **Reprodutibilidade forte desde o dia zero:** `uv.lock` + Parquet local versionável por manifesto + seeds obrigatórios em componentes estocásticos + config YAML fora do código permitem reproduzir qualquer resultado a partir de `(config, commit, dataset id)`.
- **Acoplamento frouxo protege evolução:** `strategies` depende só de `data`; regime entra como insumo **opcional** via `backtest`/`validation`; `risk` (governança) fica separado de `backtest` (simulação). Isso evita o monolito típico de frameworks de trading onde tudo vira uma classe gigante.
- **Compatibilidade com ambiente corporativo:** `uv` não exige admin, nada depende de Docker no núcleo, nenhum serviço permanente; roda em WSL2 em Windows corporativo ou em Linux/macOS.
- **Qualidade travada por CI desde cedo:** ruff + pyright + pytest bloqueando merge no GitHub Actions mínimo impede drift de qualidade antes que vire débito grande.
- **Cobertura ≥ 85% nos módulos financeiramente críticos** (`risk/`, `backtest/`, `validation/`) calibra onde o rigor importa mais; demais módulos ficam sem barra rígida inicial.

### Negative

- **vectorbt tem API peculiar e não é event-driven.** Para paper/live sofisticado no futuro, pode ser necessário introduzir uma segunda engine (ex: nautilus-trader) via novo ADR. Aceitamos este custo porque o produto **nasce como laboratório**, não como executor.
- **pandas em vez de polars** significa abrir mão de velocidade bruta em operações tabulares; aceito porque vectorbt é construído sobre o ecossistema pandas/numpy e trocar cedo multiplicaria atrito sem benefício proporcional.
- **DuckDB adiado** significa que queries ad hoc em Parquet serão feitas via pandas/pyarrow no início; se a dor aparecer, entra por novo ADR.
- **Sem GPU no núcleo** limita o teto de paralelismo; aceito porque vectorbt é CPU-bound e o hardware baseline assumido (8+ threads, 16 GB) absorve o escopo inicial.
- **Cobrir Windows nativo não é objetivo primário** — usuário em Windows corporativo precisará de WSL2.
- **Duas metas de performance ficam TBD** (pipeline end-to-end < 10 min; grid search ≥ 1.000 combinações < 2 h) — calibrar na fase `building` e revisar este ADR se os números forem irrealistas.

### Neutral

- **`metrics` não vira módulo próprio agora** — vive como subárea `scoring` dentro de `ranking`. Pode ser extraído depois sem custo alto.
- **`scripts/` é transitório** — fluxos recorrentes migram para `cli/` ou módulos internos assim que estabilizam.
- **`ccxt` fica deferred** — entra só na Fase 6 (paper/live), em novo ADR.
- **Classificador de regime começa heurístico** (ATR, ADX, volatilidade realizada); versão ML fica deferred.

## Alternatives considered

### Engine de backtest
- **Backtrader** — rejeitado porque é event-driven clássico, mais lento em varredura em massa, e o Alpha Forge é laboratório de pesquisa quantitativa, não simulador operacional.
- **nautilus-trader** — rejeitado para o início por curva de aprendizado maior e foco mais operacional; pode reaparecer em ADR posterior se o projeto crescer para paper/live sério.
- **Zipline-reloaded** — rejeitado por manutenção irregular e foco em equities tradicionais.
- **Engine próprio sobre pandas/numpy** — rejeitado por custo de oportunidade: reimplementar vectorbt não agrega edge.

### Stack tabular
- **polars** — rejeitado por atrito com vectorbt (construído sobre pandas); pode ser considerado em futuro se vectorbt ganhar suporte nativo ou se trocarmos de engine.

### Storage
- **DuckDB como storage primário** — rejeitado agora; fica como camada opcional futura de consulta sobre Parquet. Motivo: Parquet local preserva simplicidade, versionamento e portabilidade.
- **SQLite** — rejeitado por não ser colunar (ruim para datasets OHLCV longos).
- **Postgres local** — rejeitado por exigir serviço permanente, o que viola constraint ambiental.

### Dependências
- **poetry** — rejeitado por ser mais lento que `uv` e menos moderno no fluxo sync/run/lock.
- **conda** — rejeitado por peso e conflitos recorrentes em ambientes corporativos.
- **pip + requirements.txt** — rejeitado por falta de lockfile determinístico sem ferramentas extras.

### Typecheck
- **mypy** — rejeitado como default inicial por ser mais lento; fica como fallback se aparecer necessidade específica que pyright não cobrir.

### Repo layout
- **Flat layout** (`alpha_forge/` na raiz) — rejeitado em favor de **src-layout** por proteção contra import acidental do código em desenvolvimento.

### Módulos
- **Mesclar `risk` em `backtest`** — rejeitado: risk é governança/orçamento; backtest é motor de simulação. Misturar cedo produz monolito.
- **`metrics` como módulo separado agora** — rejeitado: começa como subárea de `ranking.scoring`; extrair só se crescer.
- **`strategies` dependendo de `regimes`** — rejeitado: regime é insumo opcional injetado via `backtest`/`validation`. Acoplamento direto travaria o catálogo inteiro a uma camada opcional.

### Ambiente
- **Docker no núcleo** — rejeitado por constraint de ambiente corporativo.
- **Cloud/distribuído desde o início** — rejeitado; é `deferred`, a V1 roda local com reprodutibilidade forte.

## Follow-ups

- [ ] Scaffolding do repo conforme `vision/03-architecture.md` seção "Repository shape" (pyproject.toml, src/alpha_forge/, tests/, configs/, notebooks/, .gitignore, .github/workflows/ci.yml).
- [ ] ADR-0002 — Política anti-lookahead (enforcement via infraestrutura + corpus sintético para hypothesis).
- [ ] ADR-0003 — Protocolo de validação estatística (walk-forward, OOS, Monte Carlo, perturbações de custo, flags de fragilidade).
- [ ] ADR-0004 — Política de risco e modelagem de execução (risco por trade/dia/ativo/estratégia/portfólio, equity guard, kill switch, risco de liquidação aproximada).
- [ ] ADR-0005 — Esquema de versionamento de datasets (manifesto `datasets.yaml`, detecção de gaps, bloqueio de ranking em datasets inválidos).
- [ ] ADR-0006 — Scoring multiobjetivo e pesos configuráveis.
- [ ] Calibrar na fase `building` as metas TBD: pipeline end-to-end < 10 min e grid search ≥ 1.000 combinações < 2 h. Ambas registradas como bloqueios em `STATE.md`.
