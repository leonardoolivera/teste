# `cli/` — entrypoints de linha de comando

## Responsabilidade

Expor fluxos recorrentes via CLI. Entry point declarado em `pyproject.toml`: `alpha-forge`.

## O que ainda não existe

Quase tudo. Apenas `main()` placeholder que imprime mensagem e retorna 0.

Comandos previstos (a implementar):

- `alpha-forge data download` — download de OHLCV
- `alpha-forge data validate` — validação de integridade do manifesto
- `alpha-forge backtest run` — backtest de uma estratégia
- `alpha-forge validate` — pipeline de validação (walk-forward + MC + stress)
- `alpha-forge rank` — gerar leaderboard a partir de runs

## Depende de

Todos os módulos de domínio. A CLI é cliente, não lógica.

## Primeiro arquivo real esperado

`app.py` — parser (argparse ou typer) com subcomandos vazios mas discoveráveis via `alpha-forge --help`.
