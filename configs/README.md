# `configs/`

YAMLs versionados, fora do pacote Python. Edição não exige tocar código.

## Subpastas

- **`strategies/`** — config por estratégia (parâmetros + filtros). Schema pydantic validará runtime.
- **`experiments/`** — config de experimentos (walk-forward splits, grid search, Monte Carlo).
- **`risk/`** — orçamentos de risco por trade/dia/ativo/estratégia/portfólio.
- **`regimes/`** — parâmetros do classificador heurístico.

## Regras

- Todo YAML é validado por pydantic v2 antes de ser consumido (NFR: reprodutibilidade).
- Comentários YAML são bem-vindos.
- Nada aqui contém segredos (chaves de exchange vão em `.env`, fora do repo).
