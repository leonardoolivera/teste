# IMPLEMENTATION.md - AZ.2

## Mapeamento SPEC -> execucao

Sem codigo novo: reuso completo AK. Apenas ajuste de parametros.

`alpha-forge validate --strategy bollinger --bollinger-window 30 --bollinger-num-std 1.5 --dataset-id btcusdt_1h_20240705_20241231_binance_spot --regime-filter bollinger_width:window=20:num_std=2.0:min_width_bps=250 --stress fee+10:10:0:0 --stress spread+10:0:0:10 --run-id bollinger-30-15-btc-1h-2024h2-regime-bw-250 --mc-seed 42 --mc-resamples 1000`

## Arquivos alterados

Nenhum.

## Testes executados

Suite: 368 passed, 1 skipped.

## Conformidade

- ADR-0002 causal: herdado.
- ADR-0019: fee+10 == spread+10 bit-identico.
- ADR-0022: filtro BW contrato minimal.
- ADR-0025: hit >= 45%.
- ADR-0026: Bollinger edge-triggered mantida.
