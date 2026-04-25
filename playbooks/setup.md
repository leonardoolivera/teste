# Setup — Alpha Forge local

> **Status:** validado end-to-end em **Windows 11 + Python 3.13 + pip (editable install)** — incluindo `run-demo` real sobre o dataset sintético seminal e suíte completa (`118 passed, 1 skipped` em ~30s). **Não validado:** `uv` em WSL2/Linux/macOS — o caminho `uv sync` é o recomendado pelo [`vision/03-architecture.md`](../vision/03-architecture.md) mas ainda não foi executado neste repositório em máquina real.
>
> O projeto hoje já vai além de scaffolding: tem núcleo de backtest, duas estratégias reais (MA crossover, Donchian), três datasets reais ingeridos, CLI operacional com `run-demo` e ~118 testes. O playbook abaixo leva o leitor do zero até um backtest rodando.

## Prerequisites

- **Python** 3.12 ou 3.13. O arquivo `.python-version` pina `3.12`, mas a suíte foi validada também em 3.13.7. Qualquer 3.12.x deve funcionar sem ajuste; 3.13.x funciona com o caminho `pip install --user -e .` validado.
- **Git**.
- **Um dos dois gerenciadores:**
  - **`uv`** (recomendado por `vision/03-architecture.md`) — instalação: https://docs.astral.sh/uv/. Ainda **não validado neste repo**.
  - **`pip`** (fallback validado) — já vem com Python. Este é o caminho testado neste playbook.
- **Ambiente primário:** Linux/macOS/WSL2 com `uv` conforme a vision, **ou** Windows nativo com `pip` (validado). Nenhum Docker, nenhum admin.

## 1. Clone

```bash
git clone <URL-do-repo> alpha-forge
cd alpha-forge
```

## 2. Instalar dependências

### Caminho A — `uv` (recomendado, não validado neste host)

```bash
uv sync --extra dev
```

Cria `.venv/` com deps de runtime + dev (pytest, hypothesis, ruff, pyright, jupyter).

### Caminho B — `pip` editable install (validado em Windows + Python 3.13)

```bash
pip install --user -e .
pip install --user pytest hypothesis pyarrow pyyaml
```

O editable install instala o pacote em modo desenvolvimento. As deps de `[project.optional-dependencies].dev` (ruff, pyright, jupyter, pytest-cov) **não** são instaladas automaticamente por `pip install -e .` — se você quiser rodar lint/typecheck também, adicione `pip install --user ruff pyright jupyter ipykernel`.

## 3. Verificar import do pacote

```bash
python -c "import alpha_forge; print(alpha_forge.__version__)"
```

Esperado: `0.0.0`.

## 4. Bootstrap do dataset sintético seminal

O CLI `run-demo` espera o dataset `synthetic_btcusdt_1h_seed42` presente em disco. Em clone fresco, gere-o:

```bash
python scripts/bootstrap_synthetic_dataset.py
```

Esperado: atualiza `data/datasets.yaml` com a entrada `synthetic_btcusdt_1h_seed42` (720 barras, sha256 determinístico) e grava o Parquet em `data/processed/SYNTHBTC/1h/`.

## 5. (Opcional) Ingestão de datasets reais

Para rodar `run-demo` sobre BTC/ETH/SOL 1h reais (Binance Vision):

```bash
python scripts/ingest_binance_vision.py --symbol BTCUSDT --timeframe 1h --start 2025-07-05 --end 2025-12-31
```

Substitua `BTCUSDT` por `ETHUSDT` ou `SOLUSDT` conforme o ativo desejado. Requer internet. Sem esta etapa, os `integration tests` e property-tests sobre dados reais fazem skip limpo — a suíte inteira continua verde.

## 6. Rodar o CLI real

### Com `uv` (não validado neste host)

```bash
uv run alpha-forge run-demo
```

### Com `pip` (validado)

O entry-point `alpha-forge` é criado em user scripts (`%AppData%\Python\Python313\Scripts\alpha-forge.exe` no Windows). Se essa pasta não estiver no PATH, rode via módulo:

```bash
python -c "from alpha_forge.cli.app import main; import sys; sys.argv=['alpha-forge','run-demo']; main()"
```

Saída esperada (dataset sintético, defaults MA 20/50, taker 5 bps + slippage 2 bps/notional):

```
dataset          : synthetic_btcusdt_1h_seed42
strategy         : ma_crossover short=20 long=50 long_only=True
barras           : 720
fills            : 16
equity final     : 9535.36
--- metrics ---
total_pnl        : -464.64 (-4.65%)
trade_count      : 8
hit_rate         : 12.50%
max_drawdown     : 5.46%
```

Flags úteis: `--strategy donchian --entry-window 20 --exit-window 10`; `--taker-fee-bps 0 --slippage-bps-per-notional 0` (zero cost); `--no-long-only` (MA simétrica, ADR-0012); `--log-level info|debug` (observabilidade em stderr).

## 7. Rodar a suíte de testes

### Com `uv` (não validado neste host)

```bash
uv run pytest -q
```

### Com `pip` (validado)

```bash
python -m pytest -q
```

Esperado (com dataset sintético bootstrapado na etapa 4 + pelo menos o dataset BTC ingerido na etapa 5): **`118 passed, 1 skipped`** em ~30s. O único skip é estrutural do hypothesis (`test_lookahead_guard`) e não é falha. Se algum dataset real não foi ingerido, o respectivo integration test faz skip limpo.

## 8. (Opcional) Lint + format check + typecheck

Só aplicável se você instalou o extra `dev` (caminho `uv`) ou instalou manualmente `ruff` e `pyright` (caminho `pip`):

```bash
ruff check .
ruff format --check .
pyright
```

Tudo deve passar sem erros.

## 9. (Opcional) Jupyter

```bash
jupyter lab    # ou: uv run jupyter lab
```

Notebooks vivem em `notebooks/exploratory/` e `notebooks/reports/`. Não há notebooks prontos ainda.

## Troubleshooting

- **`uv: command not found`** → instale o `uv` (https://docs.astral.sh/uv/getting-started/installation/). Alternativa válida e testada: caminho B (`pip install --user -e .`).
- **`alpha-forge: command not found` após `pip install --user -e .`** → o entry-point está em `%AppData%\Python\Python3xx\Scripts\` (Windows) ou `~/.local/bin/` (Linux/macOS), que pode não estar no PATH. Use o workaround via `python -c "from alpha_forge.cli.app import main; ..."` mostrado na etapa 6, ou adicione o diretório ao PATH.
- **`No module named alpha_forge.cli.__main__`** → `python -m alpha_forge.cli` não funciona (o subpacote não tem `__main__.py` por design). Use um dos dois caminhos da etapa 6.
- **`pyright` falha por stubs ausentes** → stubs externos (vectorbt, plotly) podem gerar warnings `reportMissingTypeStubs`, configurados como `warning` em `pyproject.toml`.
- **Import de `vectorbt` lento na primeira vez** → normal; ele pré-compila Numba na primeira execução. O núcleo próprio do projeto não depende de `vectorbt`; ele é deferred conforme ADR-0001.
- **Integration test sobre dataset real falha com `DatasetNotFoundError`** → rode a etapa 5 para o símbolo correspondente, ou ignore (o test faz skip limpo em clone fresco).

## Host de validação

| Componente        | Versão / Valor                                      |
|-------------------|------------------------------------------------------|
| SO                | Windows 11 Pro 10.0.26200                            |
| Shell             | Git Bash                                             |
| Python            | 3.13.7                                               |
| Instalação        | `pip install --user -e .` + deps manuais             |
| Resultado `pytest`| `118 passed, 1 skipped` em ~30s                      |
| Data validação    | 2026-04-17                                           |

**Ambientes ainda não validados:** `uv` em WSL2, `uv` em Linux nativo, `uv` em macOS. Quem executar em algum desses deve adicionar uma linha na tabela acima.
