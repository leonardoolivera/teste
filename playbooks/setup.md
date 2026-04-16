# Setup — Alpha Forge local

> **Status:** `# DRAFT — untested` (remover esta linha após rodar na máquina alvo).
>
> Este playbook vale para a **fase atual (scaffolding)**. Ainda não há fluxo de pesquisa funcional — o objetivo é ter o ambiente instalado, CI local passando e o pacote importável.

## Prerequisites

- **Python** 3.12 (o arquivo `.python-version` pina `3.12`; qualquer 3.12.x funciona).
- **`uv`** — gerenciador de dependências (instalação: https://docs.astral.sh/uv/).
- **Git**.
- **Ambiente primário recomendado:** WSL2 em Windows, ou Linux/macOS. Windows nativo não é suportado como ambiente principal (ver `vision/03-architecture.md`).
- **Sem Docker, sem admin.** Nada disto é necessário.

## 1. Clone

```bash
git clone <URL-do-repo> alpha-forge
cd alpha-forge
```

## 2. Instalar dependências

```bash
uv sync --extra dev
```

Isto cria `.venv/` com deps de runtime + dev (pytest, hypothesis, ruff, pyright, jupyter).

## 3. Verificar import do pacote

```bash
uv run python -c "import alpha_forge; print(alpha_forge.__version__)"
```

Esperado: `0.0.0`.

## 4. Rodar o CLI placeholder

```bash
uv run alpha-forge
```

Esperado: mensagem informando que a CLI ainda não foi implementada, exit code 0.

## 5. Rodar a suíte de testes

```bash
uv run pytest -q
```

Esperado: `1 passed` (o smoke test).

## 6. Rodar lint + format check + typecheck

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

Tudo deve passar sem erros.

## 7. (opcional) Jupyter

```bash
uv run jupyter lab
```

Notebooks vivem em `notebooks/exploratory/` e `notebooks/reports/`. Não há notebooks prontos ainda.

## Troubleshooting

- **`uv: command not found`** → instale o `uv` (https://docs.astral.sh/uv/getting-started/installation/). Em Windows corporativo, prefira a instalação via pip em user-site (`pip install --user uv`) se o instalador padrão exigir admin.
- **`pyright` falha por stubs ausentes** → rodar `uv sync --extra dev` garante as deps; stubs externos (vectorbt, plotly) podem gerar warnings `reportMissingTypeStubs`, que estão configurados como `warning` em `pyproject.toml`.
- **Import de `vectorbt` lento na primeira vez** → normal; ele pré-compila Numba na primeira execução.
