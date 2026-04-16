# system/flows.md

> **Layer:** Reality.
> **Purpose:** document user-facing and automated flows that **currently work end-to-end**.
> **Agent rule:** if a flow is documented here, it must be exercised by at least one automated test.

---

## Flow: backtest demo end-to-end (`alpha-forge run-demo`)

Primeiro fluxo de domínio do projeto. Orquestra o núcleo mínimo do começo ao fim, sem dependências externas.

- **Actor:** desenvolvedor.
- **Trigger:** `uv run alpha-forge run-demo` (ou equivalente via `python -c "from alpha_forge.cli.app import run; run(['run-demo'])"`).
- **Pré-requisitos:**
  - Dataset seminal gerado uma vez por `python scripts/bootstrap_synthetic_dataset.py` (produz Parquet + entrada em `data/datasets.yaml`).
- **Steps:**
  1. Parse de flags em `cli/app.py::run` (`--dataset-id`, `--capital`, `--fracao`, `--alavancagem`, `--taker-fee-bps`, `--slippage-bps-per-notional`, `--strategy`, `--short-window`, `--long-window`).
  2. `RiskBudget` construído com validação pydantic (rejeita fora de faixa).
  3. `CostModel` construído explicitamente a partir das flags de custo (sem default silencioso — ADR-0006).
  4. `data.loaders.load_dataset(dataset_id)` lê o manifesto, valida sha256, row_count, janela temporal e continuidade contra `declared_gaps`; devolve `pd.DataFrame` com index UTC-aware.
  5. Estratégia é instanciada via `--strategy`. Default: `MovingAverageCrossoverStrategy(short_window, long_window)` (ADR-0008, long-only, stateless). Alternativa: `DummyAlternatingStrategy()` para sanidade estrutural.
  6. `backtest.engine.run_backtest` executa o loop causal:
     - Para cada barra `t`, `window = prices[:t+1]` é passada para `strategy.decide`.
     - Execução ocorre em `t+1 open` (última barra não executa).
     - `apply_cost` ajusta o preço contra o trader (entrada e saída, ADR-0006).
     - `fixed_fractional_position_sizing` calcula tamanho; `_classify_size` decide fill vs rejection.
     - Saída de posição também registra um `Trade` com PnL pós-custo.
     - Ao final, `assert_causal(signals, closes)` e `compute_metrics` rodam obrigatoriamente.
  7. `_print_summary` imprime dataset, barras, budget, cost_model, fills, rejections, equity inicial/final/max/min e as quatro métricas (`total_pnl`, `trade_count`, `hit_rate` ou `N/A`, `max_drawdown` em %).
- **Outcome:** exit code 0, saída tabular textual em stdout. Nenhum arquivo escrito fora de `data/processed/` (que é populado pelo bootstrap, não pelo `run-demo`).
- **Covered by test:** `tests/integration/test_minimal_flow.py::test_minimal_flow` replica o fluxo com manifesto em diretório temporário.

### Output exemplo 1 — MA crossover 20/50 com custo padrão (capital 10.000, fração 0.1, alavancagem 2x, taker 5bps, slippage 2bps/notional)

```
dataset          : synthetic_btcusdt_1h_seed42
strategy         : ma_crossover short=20 long=50
barras           : 720
budget           : capital=10000.00 fracao=0.100 alavancagem_max=2.00
cost_model       : taker_fee_bps=5.00 slippage_bps/notional=2.00
fills            : 16
rejections       : 0
equity inicial   : 10000.00
equity final     : 9535.36
equity max       : 10086.29
equity min       : 9535.36
--- metrics ---
total_pnl        : -464.64 (-4.65%)
trade_count      : 8
hit_rate         : 12.50%
max_drawdown     : 5.46%
```

### Output exemplo 2 — MA crossover 20/50 com zero custo explícito (mesmo dataset e budget)

```
strategy         : ma_crossover short=20 long=50
cost_model       : taker_fee_bps=0.00 slippage_bps/notional=0.00
equity final     : 9552.13
--- metrics ---
total_pnl        : -447.87 (-4.48%)
trade_count      : 8
hit_rate         : 12.50%
max_drawdown     : 5.37%
```

Diferença entre os dois cenários quantifica o atrito aplicado pelo `CostModel` sobre a mesma estratégia. MA crossover long-only sobre série sintética com drift baixo e ruído Gaussiano é estruturalmente perdedor (ADR-0008 §8: objetivo é validar contrato, não maximizar retorno).

### Output exemplo 3 — dummy (sanidade estrutural), com custo padrão

```
strategy         : dummy (sem parâmetros)
fills            : 479
--- metrics ---
total_pnl        : -21.72 (-0.22%)
trade_count      : 239
hit_rate         : 32.22%
max_drawdown     : 6.72%
```

A dummy permanece acessível via `--strategy dummy` como ferramenta de sanidade do pipeline, reproduzindo o baseline de antes da ADR-0008.

## Flow: ingestão de dataset real de Binance Vision (ADR-0009)

- **Trigger:** `uv run python scripts/ingest_binance_vision.py --symbols BTCUSDT --timeframe 1h --start 2025-07-05 --end 2025-12-31` (multi-símbolo no mesmo comando; sem ramo especial por ativo).
- **Steps:**
  1. Normaliza cada símbolo para forma canônica única (`upper`, sem `/`, `-`, `_`, espaço).
  2. Para cada `(ano, mês)` na janela: baixa `https://data.binance.vision/data/spot/monthly/klines/<SYMBOL>/<tf>/<SYMBOL>-<tf>-YYYY-MM.zip` para `data/raw/binance_vision/<SYMBOL>/<tf>/`. Download reutiliza se arquivo local já existe; 404 é tratado como mês ainda não publicado.
  3. Descompacta, concatena, converte `open_time` (ms ou µs) em `DatetimeIndex` UTC-aware, filtra para a janela exata.
  4. Detecta gaps (buracos na grade do timeframe). Se houver gap não coberto por `--declared-gap`, apaga o Parquet (não deixa órfão) e devolve status `REJECTED_UNDECLARED_GAPS`. Operador declara e re-roda.
  5. Grava Parquet em `data/processed/<SYMBOL>/<tf>/<dataset_id>.parquet`, calcula sha256, faz upsert em `data/datasets.yaml` preservando outras entradas.
  6. Imprime resumo por símbolo: `symbol`, `timeframe`, `window`, `bars_saved`, `gaps_detected`, `dataset_id`, `sha256`, `status`, `note`.
- **Outcome:** dataset real registrado e carregável por `load_dataset`. Nenhum módulo de `src/` importa rede — código HTTP/SSL (`urllib` + `certifi`) mora só no script.
- **Primeira execução real:** BTCUSDT 1h 2025-07-05 → 2025-12-31, 4320 barras, 0 gaps, `sha256=228249e2...`. Ranges observados: close ∈ [82.207, 126.011] USD.
- **Covered by test:**
  - `tests/unit/test_ingest_binance_vision.py` (sem rede, 4 testes): normalização canônica, dois símbolos distintos não colidem em path/sha256/manifesto, gap não declarado rejeita e não deixa órfão, gap declarado passa.
  - `tests/unit/test_paths_multi_asset.py` (4 testes): `processed_dataset_path` trata `symbol`/`timeframe` como opacos; nenhum ativo é privilegiado.
  - `tests/unit/test_data_loader.py::test_loader_multi_asset_nao_colide`: dois datasets de símbolos distintos coexistem no manifesto e carregam independentemente.
  - `tests/integration/test_first_real_dataset.py`: MA 20/50 roda sobre o Parquet real; skip limpo se o arquivo ainda não foi ingerido.

## Flow: bootstrap do dataset sintético seminal

- **Trigger:** `python scripts/bootstrap_synthetic_dataset.py`.
- **Steps:**
  1. `generate_ohlcv` cria DataFrame determinístico (seed 42, 720 barras 1h, começando em 2024-01-01 UTC).
  2. Escreve Parquet em `data/processed/SYNTHBTC/1h/synthetic_btcusdt_1h_seed42.parquet`.
  3. Calcula sha256 do arquivo.
  4. Constrói `DatasetManifest` com todos os campos exigidos por ADR-0005.
  5. Atualiza `data/datasets.yaml` preservando outras entradas (chave `dataset_id` é a identidade para upsert).
- **Outcome:** Parquet em disco + manifesto atualizado. Idempotente: rodar de novo produz exatamente o mesmo sha256.
- **Covered by test:** exercitado indiretamente pelo integration test, que replica o mesmo padrão (gerar sintético → gravar Parquet → registrar manifesto → carregar).

## Flow: detecção de violação de causalidade

- **Trigger:** toda chamada de `run_backtest` e todo teste property-based.
- **Steps:**
  1. `assert_causal(signals, prices)` é chamado pelo engine ao fim do loop, sem flag de desativação.
  2. Alinha signals e prices por index; se menos de 3 pontos, retorna silenciosamente.
  3. Codifica sinais como `+1/-1/0`; computa `hit_rate` sobre retornos forward das barras com sinal ativo.
  4. Se `hit_rate > 95%` em pelo menos 10 sinais → `LookaheadViolation`.
  5. Varre `k ∈ {1, 2, 3}`; se `|corr(signal, price.shift(-k).pct_change())| > 0.95` → `LookaheadViolation`.
- **Outcome:** exceção explícita aborta qualquer pipeline contaminado. Sem warning silencioso.
- **Covered by test:** `tests/property/test_lookahead_guard.py` (hypothesis) — aceita sinal causal ruidoso, rejeita peek perfeito.

## Flow: pureza causal da `MovingAverageCrossoverStrategy`

- **Trigger:** `pytest tests/property/test_ma_crossover_causal.py`.
- **Steps:**
  1. Hypothesis gera série de closes e escolhe um `t` e um `perturb_offset` futuro.
  2. Computa `strategy.decide(prices[:t+1])` na série original.
  3. Muta apenas a barra `t + perturb_offset` (estritamente no futuro de `t`).
  4. Computa `strategy.decide(prices[:t+1])` na série mutada.
  5. Os dois sinais devem ser iguais.
- **Outcome:** propriedade falha se alguma vez a estratégia usar uma barra futura; suite verde prova que `decide` é função pura de `prices[:t+1]`.
- **Covered by test:** o próprio arquivo.

## Flow: monotonicidade de custo (property-based, ADR-0010)

- **Trigger:** `pytest tests/property/test_cost_monotonicity.py`.
- **Steps:**
  1. Hypothesis sorteia `fee_low, fee_high ∈ [0, 50]` bps e `slip_low, slip_high ∈ [0, 100]` bps/notional.
  2. `assume` que `cost_high` domina `cost_low` componente a componente, com ao menos uma desigualdade estrita.
  3. Roda `run_backtest` duas vezes com **cenário idêntico** (mesmo dataset `synthetic_btcusdt_1h_seed42`, mesma `MovingAverageCrossoverStrategy(20, 50)`, mesmo `RiskBudget`); única variável é `cost_model`.
  4. `assume(result_low.metrics.trade_count > 0)` — descarta cenários triviais (ADR-0010 §Ressalva 1).
  5. Assert: `final_equity_high - final_equity_low <= 1e-6 * capital_inicial`.
- **Outcome:** 30 exemplos × 2 backtests cada (~60 backtests), ~18s. Qualquer violação vem com mensagem rica (cost_low, cost_high, final_equity_low/high, trade_count_low/high, fills_low/high) para depuração imediata.
- **Covered by test:** o próprio arquivo.

## Flow: rejeição determinística de sizing inválido

- **Trigger:** cada tentativa de entrar em posição durante `run_backtest`.
- **Steps:**
  1. `fixed_fractional_position_sizing` devolve tamanho cru.
  2. `_classify_size` testa na ordem: `NaN`, `±inf`, `0.0`, `< 0.0`, `exposure > alavancagem_max + 1e-9`.
  3. Motivo encontrado → `Rejection` registrada, fill não acontece. Nenhum motivo → `Fill` registrado com tamanho aprovado.
- **Outcome:** resultado final do backtest contém auditoria completa (`rejections` lista, cada um com motivo, price, raw_size, signal/exec timestamps).
- **Covered by test:** `tests/unit/test_engine_reject_invalid_sizing.py` (cinco gatilhos) + `tests/unit/test_risk_sizing.py` (schema e função pura).

## Flow: smoke test do pacote

- **Actor:** desenvolvedor / CI.
- **Trigger:** `pytest` local ou push/PR no GitHub.
- **Steps:** `tests/unit/test_smoke.py::test_package_imports` importa `alpha_forge` e checa `__version__`.
- **Outcome:** sanidade do scaffolding.
- **Covered by test:** o próprio arquivo.

## Flow: pipeline mínimo de CI

- **Trigger:** push para `main` ou abertura de pull request.
- **What it does:** `ruff check` + `ruff format --check` + `pyright` + `pytest -q`.
- **Side effects:** bloqueia merge se qualquer etapa falhar.
- **Defined in:** `.github/workflows/ci.yml`.
- **Covered by test:** o próprio workflow.

## Fluxos planejados, **ainda não implementados**

Não descrever abaixo da linha até existirem em código:
- walk-forward, monte carlo, stress de custos → `vision/02-scope.md` (`validation`).
- scoring multiobjetivo e rankings → `vision/02-scope.md` (`ranking`).
- classificação de regime por barra → `vision/02-scope.md` (`regimes`).
- download de OHLCV real via ccxt (deferred).
