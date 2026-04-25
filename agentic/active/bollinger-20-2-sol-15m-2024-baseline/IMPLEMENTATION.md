# IMPLEMENTATION.md — L.1 Bollinger 20/2 SOL 15m 2024

## Dependências

Reuso puro. Zero código novo no módulo `strategies/`. **Mudança mínima:** adicionado
`"15m"` e `"30m"` em `src/alpha_forge/data/synthetic.py::TIMEFRAME_DELTAS` para
desbloquear ingestão. Sem impacto em suíte (337 passed preservado).

## Arquivos alterados (por este piloto)

- `src/alpha_forge/data/synthetic.py` — +2 linhas em `TIMEFRAME_DELTAS` (`15m`, `30m`).
- `data/datasets.yaml` — 3 novos manifestos (BTC/ETH/SOL 15m 2024-H2).

## Mapeamento SPEC → execução

- SPEC §1 → `alpha-forge validate` sobre `solusdt_15m_20240705_20241231_binance_spot`.
- SPEC §4-5 → `--strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only`.
- `--min-test-bars 200` (vs 50 default) para acomodar 4× mais barras por fold.

## Comando

```bash
alpha-forge validate --run-id bollinger-20-2-sol-15m-2024-baseline \
  --dataset-id solusdt_15m_20240705_20241231_binance_spot \
  --strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only \
  --capital 10000 --fracao 0.1 --alavancagem 2.0 \
  --taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0 \
  --n-folds 5 --scheme rolling --train-fraction 0.5 --min-test-bars 200 \
  --mc-resamples 500 --mc-seed 42 \
  --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10
```
