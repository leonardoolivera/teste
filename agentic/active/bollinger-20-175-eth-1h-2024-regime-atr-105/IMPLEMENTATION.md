# IMPLEMENTATION.md - AI.2

## Mapeamento SPEC -> execucao

Reuso puro. Zero codigo novo. `alpha-forge validate --strategy bollinger --bollinger-window 20 --bollinger-num-std 1.75 --regime-filter atr_regime:window=14:min_atr_bps=105 ...`.

## Arquivos alterados

Nenhum. Reuso total de ADR-0026 (Bollinger) + ADR-0023 (ATRRegimeFilter).

## Testes executados

`alpha-forge validate` ponta-a-ponta. Suite nao tocada (reuso puro).

## Conformidade

- ADR-0019: fee+delta bit-identico a spread+delta confirmado.
- ADR-0022/0023: regime filter neutrality/lookahead/monotonicity preservadas.
- ADR-0025: hit >= 45% hard gate.
