# `io/` — helpers transversais

## Responsabilidade

Utilidades de IO compartilhadas: leitura/escrita de Parquet, resolução de paths (pathlib), logging estruturado, carregamento de configs YAML validadas por pydantic.

## O que ainda não existe

Tudo.

## Depende de

Nada no projeto (só stdlib + libs externas).

## Primeiro arquivo real esperado

`paths.py` — resolução canônica de `data/`, `results/`, `configs/` a partir da raiz do projeto. Segundo: `logging.py` (config de logger estruturado padrão). Terceiro: `parquet.py` (wrappers sobre pyarrow/pandas).
