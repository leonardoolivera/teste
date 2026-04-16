# `data/` — módulo 1

## Responsabilidade

Ingestão, validação, normalização e versionamento de dados de mercado (OHLCV multi-ativo / multi-timeframe) para o Alpha Forge.

## O que ainda não existe

Tudo. Nenhuma função implementada. Este módulo é esqueleto.

Capabilities previstas em `vision/02-scope.md`:

- download/importação OHLCV multi-ativo
- múltiplos timeframes
- reamostragem
- detecção de gaps (NFR: 100% dos gaps > 1 candle detectados)
- validação de integridade
- datasets versionáveis (manifesto em `data/datasets.yaml`)

## Depende de

Nada (módulo-raiz). Fornece dados para `strategies`, `regimes`, `risk`, `backtest`.

## Primeiro arquivo real esperado

`schemas.py` — modelos pydantic v2 para `OHLCVBar`, `DatasetManifest`, `GapRecord`. Segundo passo: `loaders.py` (leitura de Parquet com validação de integridade).
