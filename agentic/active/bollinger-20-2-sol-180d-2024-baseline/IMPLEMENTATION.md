# IMPLEMENTATION.md — J.1 Bollinger 20/2 SOL 180d 2024

## Dependências

Reuso puro. Zero código novo. Dataset 2024-H2 ingerido via `scripts/ingest_binance_vision.py`
no mesmo comando que BTC+ETH 2024.

## Arquivos alterados (por este piloto)

Nenhum em `src/` ou `tests/`. Somente artefatos agentic + 4 JSONs de validação +
1 linha no manifesto `data/datasets.yaml` (ingestão).

## Mapeamento SPEC → execução

- SPEC §1 hipótese → `alpha-forge validate` ponta-a-ponta sobre `solusdt_1h_20240705_20241231_binance_spot`.
- SPEC §4-5 entradas/saídas → `--strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only`.
- SPEC §6-11 custos/risco → idênticos a I.1 (`--taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0 --fracao 0.1 --alavancagem 2.0`).
- SPEC critério de refutação → AUDIT.md lê `run.json`, `walk_forward.json`, `cost_stress.json` e decide sob ADR-0025.

## Comando

```bash
alpha-forge validate --run-id bollinger-20-2-sol-180d-2024-baseline \
  --dataset-id solusdt_1h_20240705_20241231_binance_spot \
  --strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only \
  --capital 10000 --fracao 0.1 --alavancagem 2.0 \
  --taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0 \
  --n-folds 5 --scheme rolling --train-fraction 0.5 --min-test-bars 50 \
  --mc-resamples 500 --mc-seed 42 \
  --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10
```

Executado em `2026-04-18T10:46:32Z`. Única diferença vs I.1: `--dataset-id` e `--run-id`.
