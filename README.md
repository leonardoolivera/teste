# Alpha Forge

> Laboratório de pesquisa, backtest rigoroso, validação estatística e ranking de estratégias de trading cripto com alavancagem de até 10x, projetado para descobrir setups agressivos sem mascarar fragilidade com overfitting.

---

## Estado

**Fase atual: scaffolding.** A árvore de módulos existe, mas nenhum código de domínio está implementado. Consulte [`STATE.md`](./STATE.md) para o estado vivo do projeto.

## Ordem de leitura para agentes

Este projeto segue o protocolo do [`agent-project-template`](https://github.com/leonardoolivera/agent-project-template). Qualquer agente de IA que for trabalhar aqui **deve**:

1. Ler [`AGENTS.md`](./AGENTS.md) primeiro — é o protocolo obrigatório.
2. Ler [`STATE.md`](./STATE.md) para entender o agora.
3. Ler [`vision/`](./vision/) para entender o alvo.
4. Ler [`system/`](./system/) para entender o que já existe.
5. Consultar [`decisions/`](./decisions/) para ADRs relevantes.

## Modelo de três camadas

| Camada | Pasta | Pergunta |
|---|---|---|
| Target | [`vision/`](./vision/) | o que queremos ser? |
| Reality | [`system/`](./system/) | o que existe agora? |
| State | [`STATE.md`](./STATE.md) | onde estamos neste momento? |

A separação é estrita. `vision/` nunca descreve código existente. `system/` nunca descreve aspirações.

## Estrutura do repositório

```
src/alpha_forge/      # pacote Python (7 módulos de domínio + cli + io)
tests/                # unit / integration / property / fixtures
configs/              # YAMLs de estratégias, experimentos, risco, regimes
notebooks/            # Jupyter (exploratório e reports)
data/                 # OHLCV bruto e processado (fora do git, exceto manifesto)
results/              # runs, validação, rankings (fora do git)
scripts/              # utilitários transitórios
vision/               # alvo
system/               # realidade
decisions/            # ADRs imutáveis
playbooks/            # guias operacionais
```

Detalhes em [`vision/03-architecture.md`](./vision/03-architecture.md).

## Stack

Python 3.12+ · vectorbt · pandas · numpy · scipy · pydantic v2 · pyyaml · pytest + hypothesis · matplotlib + plotly · Jupyter · ccxt (deferred) · Parquet local · uv · ruff · pyright · GitHub Actions.

Decisões fundamentais registradas em [`decisions/0001-foundational-stack-and-architecture.md`](./decisions/0001-foundational-stack-and-architecture.md).

## Setup

Ver [`playbooks/setup.md`](./playbooks/setup.md).

Resumo:

```bash
uv sync --extra dev
uv run pytest -q
uv run alpha-forge
```

## Princípios

1. Honestidade estatística sobre performance bonita.
2. Custo real antes de retorno bruto.
3. Sem lookahead, nunca.
4. Ranking multiobjetivo, não monobjetivo.
5. Reproduzível ou não aconteceu.
6. Flags explícitas de fragilidade.
7. Agressividade com controles duros, nunca sem eles.
8. Preferir simples e auditável a sofisticado e opaco.

Detalhes em [`vision/01-product.md`](./vision/01-product.md).

## Licença

Proprietary. Uso interno. Sem warranty. O laboratório mede; não garante retornos.
