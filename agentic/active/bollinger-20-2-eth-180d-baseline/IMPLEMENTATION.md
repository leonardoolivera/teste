# IMPLEMENTATION.md — I.3 Bollinger 20/2 ETH 180d

## Dependências

Reuso puro. Zero código novo.

## Arquivos alterados (por este piloto)

Nenhum em `src/` ou `tests/`. Somente artefatos agentic e 4 JSONs de validação.

## Mapeamento SPEC → execução

- SPEC §1 hipótese → `alpha-forge validate` ponta-a-ponta sobre `ethusdt_1h_20250705_20251231_binance_spot`.
- SPEC §4-5 entradas/saídas → `--strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only`.
- SPEC §6-11 custos/risco → `--taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0 --fracao 0.1 --alavancagem 2.0`.
- SPEC critério de refutação → AUDIT.md lê `run.json`, `walk_forward.json`, `cost_stress.json` e decide sob ADR-0025.

## Comando

```bash
alpha-forge validate --run-id bollinger-20-2-eth-180d-baseline \
  --dataset-id ethusdt_1h_20250705_20251231_binance_spot \
  --strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only \
  --capital 10000 --fracao 0.1 --alavancagem 2.0 \
  --taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0 \
  --n-folds 5 --scheme rolling --train-fraction 0.5 --min-test-bars 50 \
  --mc-resamples 500 --mc-seed 42 \
  --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10
```

Executado em `2026-04-18T10:33:10Z`. Única diferença vs I.2 BTC: `--dataset-id` e `--run-id`.
