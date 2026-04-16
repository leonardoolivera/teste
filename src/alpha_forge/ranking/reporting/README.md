# `ranking/reporting/` — subárea de reporting

## Responsabilidade

Relatórios comparativos (estratégia vs estratégia, regime vs regime) e export (HTML/Parquet/CSV).

## O que ainda não existe

Tudo.

## Depende de

`ranking/scoring/` (consome scores) e `regimes` (para cortes por regime).

## Primeiro arquivo real esperado

`templates.py` (templates estáticos matplotlib) → `comparative.py` (diffs lado-a-lado) → `export.py` (HTML/Parquet/CSV).
