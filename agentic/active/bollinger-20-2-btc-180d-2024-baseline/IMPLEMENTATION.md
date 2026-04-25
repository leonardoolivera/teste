# IMPLEMENTATION.md — J.2 Bollinger 20/2 BTC 180d 2024

## Dependências

Reuso puro. Zero código novo.

## Arquivos alterados (por este piloto)

Nenhum em `src/` ou `tests/`. Apenas artefatos agentic + 4 JSONs.

## Mapeamento SPEC → execução

- SPEC §1 hipótese → `alpha-forge validate` sobre `btcusdt_1h_20240705_20241231_binance_spot`.
- SPEC §4-5 → `--strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only`.
- SPEC custos → idênticos a I.2.

## Comando

Idêntico a I.2 com `--dataset-id btcusdt_1h_20240705_20241231_binance_spot`.
