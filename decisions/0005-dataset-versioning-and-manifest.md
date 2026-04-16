# 0005 — Versionamento e manifesto de datasets (núcleo mínimo)

**Status:** Accepted
**Date:** 2026-04-16
**Deciders:** Usuário (owner do projeto) + agente.

## Context

O núcleo mínimo precisa carregar e processar séries OHLCV. Sem uma regra clara de onde os dados vivem, como são identificados e como gaps/buracos são declarados, qualquer backtest futuro fica contaminado por ambiguidade: "esse resultado foi sobre qual dataset?" deixa de ter resposta reproduzível. ADR-0001 fixou Parquet local como formato-fonte oficial, mas não detalhou o manifesto.

Esta ADR define o mínimo indispensável para rodar o núcleo funcional reprodutivelmente. **Não** cobre download automatizado, múltiplos exchanges, nem armazenamento em nuvem — tudo isso é `deferred`.

## Decision

Todo dataset OHLCV usado pelo Alpha Forge é:

1. **Armazenado** como Parquet em `data/processed/<symbol>/<timeframe>/<dataset_id>.parquet`, onde `dataset_id` é um slug estável (ex.: `btcusdt_1h_2020-01-01_2024-12-31_binance`).
2. **Registrado** em `data/datasets.yaml` (manifesto versionado em git). Campos mínimos obrigatórios (intenção registrada aqui; implementação pode ser gradual mas nenhum destes pode ser omitido quando publicado):
   - `dataset_id` — slug estável e único.
   - `symbol` — ex.: `BTCUSDT`.
   - `timeframe` — ex.: `1h`, `15m`.
   - `path` — relativo a `data/processed/`.
   - `sha256` — hash do arquivo Parquet.
   - `row_count` — número de barras.
   - `start_ts` — timestamp da primeira barra (ISO-8601 com timezone).
   - `end_ts` — timestamp da última barra (ISO-8601 com timezone).
   - `timezone` — timezone canônico do dataset (ex.: `UTC`).
   - `declared_gaps: []` — lista de intervalos ausentes conhecidos.
   - `source` — origem (ex.: `binance-spot`, `synthetic`).

   `row_count`, `start_ts` e `end_ts` são essenciais para detectar dataset "parecido mas não igual" antes mesmo de comparar sha256.
3. **Imutável**: um `dataset_id` uma vez publicado não muda de conteúdo. Correção → novo `id`.
4. **Gaps declarados explicitamente** no campo `declared_gaps` do manifesto. Um dataset com gaps não declarados (detectados por um checker de continuidade no loader) é **rejeitado no carregamento**, e bloqueia qualquer ranking que o use.

O módulo `data/` é o único autorizado a ler `datasets.yaml` e a entregar DataFrames ao resto do sistema.

## Consequences

- **Positive:** qualquer resultado pode ser reconstituído a partir do par `(dataset_id, config)`; sha256 fecha a porta para silent corruption; gaps viram dado de primeira classe, não nota de rodapé.
- **Negative:** custo manual para registrar cada dataset novo no YAML; qualquer refetch exige novo `id`, o que pode parecer burocrático no começo.
- **Neutral:** o formato YAML é versionado em git, então o histórico de datasets fica rastreável; o diretório `data/processed/` fica fora do git (já em `.gitignore`).

## Alternatives considered

- **DuckDB como fonte** — rejeitado para esta fase: ADR-0001 decidiu Parquet local como oficial; DuckDB fica opcional no futuro.
- **Fingerprint só pelo caminho do arquivo** — rejeitado: não detecta corruption nem edições silenciosas.
- **Não ter manifesto, inferir do diretório** — rejeitado: perde-se metadados críticos (source, gaps, janela temporal exata) e reproducibilidade.
- **Manifesto por dataset (um YAML ao lado do parquet)** — rejeitado nesta fase: adiciona dispersão sem ganho prático enquanto o número de datasets é baixo; pode ser reconsiderado depois.

## Follow-ups

- Implementar `src/alpha_forge/data/schemas.py` com `OHLCVBar`, `DatasetManifest`, `GapRecord` (pydantic v2).
- Implementar `src/alpha_forge/data/loaders.py` com `load_dataset(dataset_id) -> pd.DataFrame` que valida sha256, lê gaps e checa continuidade.
- Popular `data/datasets.yaml` com o primeiro dataset sintético (gerado por `data/synthetic.py`) para permitir que o núcleo rode sem download real.
- Teste unitário: carregar um dataset com gap não declarado deve levantar exceção explícita.
