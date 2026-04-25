# IMPLEMENTATION.md - AK.5

## Mapeamento SPEC -> execucao

Implementacao nova: `BollingerWidthFilter` em `src/alpha_forge/regimes/filter.py` (extensao aditiva ADR-0022, pre-autorizada em §Consequences). Parser de `--regime-filter` estendido. `alpha-forge validate --strategy bollinger --bollinger-num-std 1.5 --regime-filter bollinger_width:window=20:num_std=1.5:min_width_bps=250 ...`.

## Arquivos alterados

- `src/alpha_forge/regimes/filter.py`: +BollingerWidthFilter +canonical_string +parser.
- `src/alpha_forge/regimes/__init__.py`: export BollingerWidthFilter.
- `tests/property/test_bollinger_width_filter_lookahead.py`: novo (causal).
- `tests/property/test_bollinger_width_filter_monotonicity.py`: novo (monotonicity em min_width_bps).

## Testes executados

Suite: 368 passed, 1 skipped (+2 novos property tests).

## Conformidade

- ADR-0002 causal: coberto por test_bollinger_width_filter_lookahead.
- ADR-0019: fee+delta=spread+delta bit-identico.
- ADR-0022: contrato minimal RegimeFilter satisfeito; extensao aditiva pre-autorizada.
- ADR-0025: hit >= 45%.
