# IMPLEMENTATION.md — J.3 Bollinger 20/2 ETH 180d 2024

## Dependências

Reuso puro. Zero código novo.

## Arquivos alterados (por este piloto)

Nenhum em `src/` ou `tests/`.

## Mapeamento SPEC → execução

- SPEC §1 → `alpha-forge validate` sobre `ethusdt_1h_20240705_20241231_binance_spot`.
- SPEC §4-5 → `--strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only`.

## Comando

Idêntico a I.3 com `--dataset-id ethusdt_1h_20240705_20241231_binance_spot`.
