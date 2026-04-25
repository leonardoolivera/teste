# IMPLEMENTATION.md - AJ.5

## Mapeamento SPEC -> execucao

Reuso puro. `alpha-forge validate --strategy bollinger --bollinger-num-std 1.5 --regime-filter atr_regime:window=14:min_atr_bps=120 ...`.

## Arquivos alterados

Nenhum. Reuso total ADR-0026 + ADR-0023.

## Testes executados

`alpha-forge validate` ponta-a-ponta.

## Conformidade

ADR-0019 / 0022 / 0023 / 0025.
