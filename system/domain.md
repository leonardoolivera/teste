# system/domain.md

> **Layer:** Reality.
> **Purpose:** describe the entities and business rules that **currently exist in the code**.
> **Agent rule:** this file is a mirror of the code. If the code changes, this file changes in the same commit. If this file describes something that is not in the code, delete it.

---

## Escopo atual

Núcleo mínimo implementado (ADR-0001/0002/0004/0005). Nenhum módulo de validação, ranking, regimes ou métricas avançadas está presente — isso é `vision/`, não realidade.

Abaixo estão as entidades que **existem no código**, com suas invariantes de primeira classe.

## Data (`alpha_forge.data`)

### `OHLCVBar` (`data/schemas.py`)
Contrato lógico de uma barra. Pydantic v2, `frozen`, `extra="forbid"`.
- `timestamp: datetime`
- `open, high, low, close: float > 0`
- `volume: float ≥ 0`
- Invariantes validadas:
  - `high ≥ max(open, close)`
  - `low ≤ min(open, close)`
  - `high ≥ low`

### `GapRecord` (`data/schemas.py`)
Intervalo ausente declarado no manifesto. Frozen.
- `start, end: datetime` (inclusivos), `end ≥ start`
- `reason: str` (default `""`)

### `DatasetManifest` (`data/schemas.py`)
Entrada única do manifesto (ADR-0005). Frozen, campos exigidos:
- `dataset_id, symbol, timeframe, path, timezone, source` — strings não vazias
- `sha256` — exatamente 64 chars
- `row_count: int > 0`
- `start_ts, end_ts: datetime`, `end_ts ≥ start_ts`
- `declared_gaps: list[GapRecord]` (default `[]`)

### Geração sintética (`data/synthetic.py`)
`generate_ohlcv(start, periods, timeframe, initial_price, drift, volatility, seed) -> pd.DataFrame`.
Determinística dada a tupla de parâmetros. Timeframes suportados: `1h`, `4h`, `1d`. Index UTC-aware com nome `timestamp`. Colunas `open, high, low, close, volume`.

### Loader (`data/loaders.py`)
`load_dataset(dataset_id, manifest_path=None) -> pd.DataFrame`.
Falha determinística (`DatasetIntegrityError`) quando:
- arquivo ausente em `data/processed/<path>`
- sha256 calculado ≠ manifesto
- index não é `DatetimeIndex` UTC-aware
- `row_count`, `start_ts` ou `end_ts` divergem do manifesto
- há gaps não cobertos por `declared_gaps`

Único ponto autorizado a ler `data/datasets.yaml`.

## Risk (`alpha_forge.risk`)

### `RiskBudget` (`risk/schemas.py`)
Governança mínima por execução (ADR-0004). Frozen.
- `capital_inicial: float > 0`
- `fracao_por_trade: float ∈ (0, 1]`
- `alavancagem_max: float ∈ [1.0, 10.0]` — **hard cap**, não sugestão

### `fixed_fractional_position_sizing` (`risk/sizing.py`)
Função pura, determinística, sem I/O:
`(capital_corrente * fracao_por_trade * alavancagem_max) / preco_entrada`.
Retorna `0.0`, `NaN` ou `±inf` diante de inputs patológicos (preço zero, capital zero) — **não** levanta exceção. A decisão de rejeitar é do engine.

## Backtest (`alpha_forge.backtest`)

### `Signal` (`backtest/schemas.py`)
Enum: `ENTER_LONG`, `ENTER_SHORT`, `EXIT`, `HOLD`.

### `Side` (`backtest/schemas.py`)
Enum: `LONG`, `SHORT`, `FLAT`.

### `Fill` (`backtest/schemas.py`)
Execução efetiva em `t+1 open`. Frozen.
- `timestamp: datetime` (execução)
- `signal_timestamp: datetime` (emissão do sinal)
- `side: Side`, `price: float`, `size: float`, `notional: float`

Invariante estrutural (ADR-0002): **`timestamp > signal_timestamp` sempre**.

### `Rejection` / `RejectionReason` (`backtest/schemas.py`)
Ordem não executada por sizing inválido (ADR-0004). Motivos possíveis:
- `SIZE_ZERO`
- `SIZE_NEGATIVE`
- `SIZE_NAN`
- `SIZE_INF`
- `ABOVE_LEVERAGE_CAP`

### `CostModel` (`backtest/cost.py`, ADR-0006 + ADR-0019)
Contrato de custos por execução de backtest. Frozen.
- `taker_fee_bps: float ≥ 0` — fee base em basis points.
- `slippage_bps_per_unit_notional: float ≥ 0` — slippage linear por unidade de `notional/capital_inicial`.
- `spread_bps: float ≥ 0` (default `0.0`, ADR-0019) — half-spread estrutural em bps aplicado contra o trader em cada fill, **independente de notional**. Default zero preserva bit-a-bit o comportamento da ADR-0006.
Helper `zero_cost()` devolve `CostModel(0.0, 0.0)` para uso explícito (spread_bps herda default 0.0). Função pura `apply_cost(...)` aplica o ajuste **contra o trader** no preço (não no PnL): entrada long e saída short pagam preço mais caro; saída long e entrada short recebem preço mais barato. Fórmula: `total_bps = taker_fee_bps + slippage_bps_per_unit_notional * (notional / capital_inicial) + spread_bps`.

### `Trade` (`backtest/schemas.py`, ADR-0007)
Par fechado (entrada, saída). Frozen.
- `side: Side`, `entry_timestamp, exit_timestamp: datetime`
- `entry_price, exit_price, size, pnl: float`
Entrada sem saída correspondente até o fim do backtest **não** gera `Trade`. Seu PnL mark-to-market entra via `final_equity`.

### `BacktestMetrics` (`backtest/schemas.py`, ADR-0007)
Frozen.
- `total_pnl: float` — absoluto, `final_equity - capital_inicial`.
- `trade_count: int ≥ 0` — só trades fechados.
- `hit_rate: float | None` — fração ∈ [0, 1], **`None` quando `trade_count == 0`** (nunca `0.0` nem `NaN`).
- `max_drawdown: float ∈ [0, 1]` — `max(1 - equity/running_max)`, `0.0` se curva não cair.
Computado por `compute_metrics(result, capital_inicial)` em `backtest/metrics.py`. Vive em `backtest/`, não em `ranking/scoring/` — caracterização de backtest, não comparação entre estratégias.

### `BacktestResult` (`backtest/schemas.py`)
- `dataset_id: str`
- `bars: int ≥ 0`
- `fills: list[Fill]`, `rejections: list[Rejection]`, `trades: list[Trade]`
- `final_equity, max_equity, min_equity: float`
- `equity_curve: list[(datetime, float)]`
- `metrics: BacktestMetrics | None` — preenchido pelo engine no fim de `run_backtest`.

### `assert_causal` / `LookaheadViolation` (`backtest/lookahead_guard.py`)
Heurística de enforcement (ADR-0002):
- Mapeia sinais para `+1/-1/0`.
- Levanta `LookaheadViolation` quando `hit_rate(sign(signal) * forward_return) > 95%` em amostra de pelo menos 10 sinais ativos.
- Levanta `LookaheadViolation` quando `|corr(signal, price.shift(-k).pct_change())| > 0.95` para `k ∈ {1, 2, 3}`.

### `run_backtest` (`backtest/engine.py`)
Assinatura: `run_backtest(*, prices, strategy, budget, cost_model, dataset_id) -> BacktestResult`. `cost_model` é **obrigatório** (ADR-0006); sem default silencioso.

Loop causal explícito:
1. Para cada barra `t`: `signal = strategy.decide(prices[:t+1])` (Contrato A — janela causal).
2. Execução em `t+1 open` (última barra não executa).
3. `apply_cost` ajusta o preço contra o trader (entrada e saída).
4. `fixed_fractional_position_sizing` → classificador determinístico `_classify_size` → fill ou rejection.
5. Fechamento de posição emite `Fill` (side=FLAT) **e** um `Trade` com PnL pós-custo.
6. Ao fim, `assert_causal(signals, closes)` obrigatório e `compute_metrics` preenche `result.metrics`.

**Reverse-on-signal (ADR-0012):** se há posição aberta e chega `ENTER_LONG`/`ENTER_SHORT` na **direção oposta**, o engine fecha a posição atual e abre a nova, ambas em `t+1 open`. Registra dois `Fill` com a mesma `timestamp` (um de fechamento side=FLAT, um de abertura) e um `Trade` fechado. **Custo é aplicado duas vezes** — fechar e abrir são duas operações de mercado. Sinal de entrada na mesma direção da posição existente continua sendo no-op.

Única posição aberta por vez no núcleo mínimo. Equity a cada barra: `capital_inicial + PnL_realizado_dos_trades_fechados + PnL_unrealized_da_posicao_aberta`.

## Strategies (`alpha_forge.strategies`)

### `Strategy` (`strategies/base.py`)
ABC. Único método: `decide(window: pd.DataFrame) -> Signal`. Contrato estrutural: estratégia recebe **apenas** `prices[:t+1]` — sem acesso ao dataset completo.

### `DummyAlternatingStrategy` (`strategies/families/dummy/strategy.py`)
Implementação trivial para validar pipeline. Compara as duas últimas closes:
- subiu → `ENTER_LONG`
- caiu → `ENTER_SHORT`
- empate → `HOLD`
Ao inverter direção, emite `EXIT` antes da próxima entrada. Mantém `_last_signal` como estado interno mínimo. **Não é estratégia séria.** Permanece disponível como ferramenta de sanidade estrutural (acessível via `--strategy dummy` na CLI).

### `DonchianBreakoutStrategy` (`strategies/families/donchian/strategy.py`, ADR-0011 + ADR-0013)
Segunda estratégia real. Parâmetros: `entry_window: int > 0`, `exit_window: int > 0`, `long_only: bool = True` — sem restrição de ordenação entre as janelas e sem defaults no construtor (exceto `long_only`). Validação cedo e explícita: `TypeError` para não-inteiros em `entry_window`/`exit_window` (inclui `bool` e `float` que "é inteiro") ou qualquer não-`bool` em `long_only` (rejeita `int`, `None`, `str`); `ValueError` para valores não positivos. Default `long_only=True` preserva o contrato ADR-0011 bit-a-bit para callers existentes.

Regra (ADR-0011 §"Regra exata" + ADR-0013):
Eventos observáveis (inalterados por ADR-0013):
- Breakout bullish: `high[t-1] > max(high[t-entry_window-1 : t-1])`.
- Breakout bearish: `low[t-1] < min(low[t-exit_window-1 : t-1])`.

Mapeamento depende de `long_only`:
- `long_only=True` (default): bullish → `ENTER_LONG`; bearish → `EXIT`; ambos simultâneos → `EXIT` (ADR-0011).
- `long_only=False` (ADR-0013): bullish → `ENTER_LONG`; bearish → `ENTER_SHORT`; ambos simultâneos → `ENTER_SHORT` (arbitragem conservadora espelhada). **Não emite `EXIT`** — fechamento via reversão coordenada pelo engine (ADR-0012, custo duplo).
- Desigualdades **estritas**: empate exato não é sinal.
- Warm-up: `HOLD` enquanto `len(window) < max(entry_window, exit_window) + 2`.

A janela de comparação **exclui** a barra `t-1` (é o max/min das `N` barras anteriores a `t-1`). A estratégia ignora `window.iloc[-1]` (barra `t`) por construção — mesmo que o engine já garanta causalidade, o código da estratégia fica inequivocamente causal na leitura.

**Stateless.** `decide(window) -> Signal` é função pura de `window` e parâmetros. Redução a no-op por sinais redundantes (`ENTER_LONG` com posição aberta, `EXIT` sem posição) é responsabilidade do engine.

### `MovingAverageCrossoverStrategy` (`strategies/families/ma_crossover/strategy.py`, ADR-0008 + ADR-0012)
Primeira estratégia real. Parâmetros: `short_window: int`, `long_window: int`, `long_only: bool = True`, com `0 < short_window < long_window`. Validação cedo e explícita: `ValueError` para inteiros não positivos ou `short_window >= long_window`; `TypeError` para não-inteiros (inclui `bool`) em `short_window`/`long_window`, ou qualquer não-`bool` em `long_only` (rejeita `int`, `None`, `str`). SMA sobre coluna `close`. Default `long_only=True` preserva o contrato ADR-0008 bit-a-bit para callers existentes.

Regra (ADR-0008 §4 + ADR-0012):
- Cross-up: `short_ma[t] > long_ma[t]` **e** `short_ma[t-1] <= long_ma[t-1]`.
- Cross-down: `short_ma[t] < long_ma[t]` **e** `short_ma[t-1] >= long_ma[t-1]`.
- Mapeamento depende de `long_only`:
  - `long_only=True` (default): cross-up → `ENTER_LONG`; cross-down → `EXIT`.
  - `long_only=False`: cross-up → `ENTER_LONG`; cross-down → `ENTER_SHORT`. **Sem `EXIT`** — reversões são resolvidas pelo engine (ver `run_backtest` abaixo).
- Qualquer outro caso → `HOLD`. Empate exato não é sinal.
- Warm-up: `HOLD` enquanto `len(window) < long_window + 1`. Sem `fillna`, sem preenchimento mágico.

**Stateless.** `decide(window) -> Signal` é função pura de `window` e parâmetros. O engine é quem mantém o estado "em posição ou não"; a estratégia só emite intenção. `ENTER_LONG` com posição aberta na mesma direção vira no-op; sinal de entrada na direção **oposta** vira reverse-on-signal (ver `run_backtest`).

## Validation (`alpha_forge.validation`, ADR-0003 + ADR-0014 + ADR-0015 + ADR-0017)

Três contratos funcionais no núcleo mínimo (walk-forward causal, Monte Carlo sobre trades, stress de custos sistematizado) + camada passiva de persistência (grava/lê quatro artefatos em JSON versionado: três relatórios de pipeline + metadados de corrida). Tudo o mais (tuning, composite scoring, ranking, flags de fragilidade, perturbações multiplicativas, stress de preço/dataset/hiperparâmetros, compressão, migração entre versões de schema) permanece segurado até ADRs próprias.

### `WalkForwardWindow` / `WalkForwardFold` (`validation/schemas.py`)
- `WalkForwardWindow(start: datetime, end: datetime, bars: int ≥ 0)`
- `WalkForwardFold(fold_index: int ≥ 0, train_window: WalkForwardWindow, test_window: WalkForwardWindow, result: BacktestResult)`
- Ambos frozen. `result` é produzido por `run_backtest` sobre `test_window` — causalidade herdada por construção.

### `walk_forward` (`validation/walk_forward.py`)
Divide `prices` em `n_folds` janelas de teste contíguas e disjuntas; executa `run_backtest` em cada `test_window` com a estratégia fixa. Scheme `rolling` usa janela proporcional de treino; `expanding` sempre desde o início. Fold 0 pulado (sem train prévio). Nenhum tuning — tuning vira ADR separada. Levanta `ValidationError` para parâmetros inválidos ou dataset curto.

### `MonteCarloSummary` (`validation/schemas.py`)
- `n_resamples: int ≥ 100`
- `seed: int` obrigatório
- `final_equity_percentiles: dict[int, float]` — chaves fixas `{5, 25, 50, 75, 95}`
- `max_drawdown_percentiles: dict[int, float]` — mesmas chaves
- `original_final_equity: float`, `original_max_drawdown: float`

### `monte_carlo_trades` (`validation/monte_carlo.py`)
Reamostra com reposição a lista de PnLs de `result.trades`, recomputa curva de equity e `max_drawdown` em cada amostra. `numpy.random.default_rng(seed)` para determinismo bit-a-bit. **Assume i.i.d. de PnL por trade** — limitação declarada; bootstrap em blocos é deferred.

### `CostPerturbation` / `CostStressCell` / `CostStressReport` (`validation/schemas.py`, ADR-0014)
- `CostPerturbation(label: str min_length=1, fee_delta_bps: float ≥ 0, slip_delta_bps: float ≥ 0, spread_delta_bps: float ≥ 0 default 0.0)` — delta **absoluto aditivo** em bps sobre o `CostModel` baseline. Não-negativo por contrato; stress aumenta custo contra o trader. `spread_delta_bps` (ADR-0019) tem default zero para retrocompat com perturbações pré-E.9; payloads JSON antigos carregam com `spread_delta_bps=0.0` automaticamente.
- `CostStressCell(scenario_index: int ≥ 0, label, cost: CostModel, result: BacktestResult, final_equity: float, final_equity_delta_vs_baseline: float)` — uma linha do relatório.
- `CostStressReport(dataset_id, baseline: CostStressCell, scenarios: list[CostStressCell] min_length=1)` — baseline (`scenario_index=0`) + cenários perturbados (`scenario_index ≥ 1` na ordem da lista).
- Todos frozen + `extra="forbid"`.

### `cost_stress` (`validation/cost_stress.py`, ADR-0014)
Roda `N+1` backtests (baseline + N perturbações) sobre o mesmo `(prices, strategy, budget, dataset_id)`. Cada perturbação vira `effective_cost = baseline + delta` nos três componentes (fee + slip + spread, ADR-0019). Baseline sai com `dataset_id` original; cenários perturbados recebem sufixo `#stress{k}` (análogo ao `#fold{k}` do walk-forward) para auditabilidade. **Assert-a ADR-0010 por cenário antes de devolver**: `final_equity_delta_vs_baseline ≤ 1e-6 * capital_inicial`; violação levanta `ValidationError` (é bug do engine, não flakiness). Validações eager: `perturbations` não-vazio, pelo menos uma perturbação estritamente positiva em **qualquer** dos três componentes, labels únicos.

### Persistência (`validation/persistence.py`, ADR-0015 + ADR-0017)
Camada passiva que grava e carrega quatro artefatos em JSON versionado dentro de `results/validation/<run_id>/`: os três relatórios de pipeline (`WalkForwardFold[]`, `MonteCarloSummary`, `CostStressReport`) e os metadados de corrida (`RunMetadata`). Arquivos fixos: `walk_forward.json`, `monte_carlo.json`, `cost_stress.json`, `run.json`. Envelope `{"schema_version": "1", "payload": ...}` — versão é string, incompatibilidade levanta `ValidationError` (sem migração). Sobrescrita é permitida; cada relatório é opcional. Funções: `save_walk_forward_folds`/`load_walk_forward_folds`, `save_monte_carlo_summary`/`load_monte_carlo_summary`, `save_cost_stress_report`/`load_cost_stress_report`, `save_run_metadata`/`load_run_metadata`. Round-trip bit-a-bit garantido (testado). `io/paths.py::validation_run_dir(run_id)` devolve o caminho canônico. `walk_forward`, `monte_carlo_trades` e `cost_stress` **não** foram alterados — persistência consome os objetos por composição.

### `RunMetadata` (`validation/schemas.py`, ADR-0017)
Frozen + `extra="forbid"`.
- `alpha_forge_version: str min_length=1` — `alpha_forge.__version__` capturado no momento da corrida.
- `timestamp_utc: datetime` — timezone-aware UTC (gerado por seam `cli.app._now_utc`, injetável em testes).
- `command: str min_length=1` — nome do subcomando da CLI (atualmente só `"validate"`).
- `run_id: str min_length=1` — mesmo `run_id` do diretório (redundância proposital para auditoria por grep).
- `flags: dict[str, str]` — todos os parâmetros de `argparse.Namespace` exceto `command`, coagidos a string (listas via `repr`). Union heterogêneo foi rejeitado na ADR-0017 §"Alternatives" para estabilidade de schema.

A CLI `validate` grava `run.json` **antes** do pipeline (rastro sobrevive abort); artefatos de pipeline abortado não são gravados, mas `run.json` permanece como trilha de auditoria.

## CLI (`alpha_forge.cli`)

Dois subcomandos em `cli/app.py`: `run-demo` (backtest único + summary) e `validate` (pipeline completo de `validation/` + persistência). Flags de dataset/risk/cost/strategy/log são compartilhadas entre os dois via helpers `_add_shared_*` — duplicação zero. Subcomando desconhecido → `parser.error` com exit 2.

### `run-demo` (ADR-0008/0011/0012/0013)
Orquestra: `load_dataset` → `RiskBudget` → `CostModel` → estratégia (escolhida por `--strategy`, default `ma_crossover`) → `run_backtest` → `_print_summary`. Sem lógica de domínio escondida na CLI.

Flags: `--dataset-id`, `--capital`, `--fracao`, `--alavancagem`, `--taker-fee-bps`, `--slippage-bps-per-notional`, `--spread-bps` (ADR-0019, default `0.0`), `--strategy {ma_crossover,dummy,donchian}`, `--short-window`, `--long-window` (MA crossover), `--entry-window`, `--exit-window` (Donchian), `--long-only/--no-long-only` (aplicável a MA crossover **e** Donchian), `--log-level`. Flags específicas de uma estratégia são ignoradas quando outra está ativa. Default: `--long-only` (MA preserva ADR-0008; Donchian preserva ADR-0011). `--no-long-only` ativa modo simétrico com shorts: ADR-0012 para MA; ADR-0013 para Donchian; reversões são coordenadas pelo engine via reverse-on-signal (custo duplo em ambas as famílias).

### `validate` (ADR-0016 + ADR-0017)
Orquestra `walk_forward` (ADR-0003) + `monte_carlo_trades` (ADR-0003, opcional) + `cost_stress` (ADR-0014, opcional) sobre um `run_id` opaco fornecido pelo chamador, e persiste via ADR-0015 em `results/validation/<run_id>/`. **Antes** de qualquer backtest, grava `run.json` com `RunMetadata` (ADR-0017) — rastro de auditoria sobrevive abort por `ValidationError` ou `DatasetIntegrityError` no meio do pipeline.

Flags compartilhadas (dataset + risk + cost + strategy + log_level): idem `run-demo` (inclui `--spread-bps`, ADR-0019). Flags específicas: `--run-id` (obrigatória, string opaca), `--n-folds`, `--scheme {rolling,expanding}`, `--train-fraction`, `--min-test-bars`, `--mc-resamples`, `--mc-seed`, `--stress label:fee_delta_bps:slip_delta_bps[:spread_delta_bps]` (3 ou 4 partes, ADR-0019; repetível), `--skip-monte-carlo`, `--skip-cost-stress`. Cada artefato de pipeline é independente (mesmo contrato da ADR-0015). Helper público `parse_stress_specs` é exportado para testes/notebooks. Seam `cli.app._now_utc` pode ser monkeypatch para fixar `timestamp_utc` em testes.

## IO (`alpha_forge.io`)

### `paths.py`
Resolução canônica de caminhos: `project_root`, `data_dir`, `data_processed_dir`, `datasets_manifest_path`, `processed_dataset_path(symbol, timeframe, dataset_id)`, `results_dir`, `results_runs_dir`.

## Datasets cadastrados

Entradas de `data/datasets.yaml`:

**`synthetic_btcusdt_1h_seed42`** — seminal sintético, gerado por `scripts/bootstrap_synthetic_dataset.py`.
- 720 barras 1h começando em 2024-01-01 UTC, seed 42, drift 0.0002, volatilidade 0.01
- `symbol: SYNTHBTC`, `source: synthetic`, `declared_gaps: []`
- Regenerável de forma determinística a partir da seed.

**`btcusdt_1h_20250705_20251231_binance_spot`** — primeiro recorte real (ADR-0009), ingerido por `scripts/ingest_binance_vision.py`.
- 4320 barras 1h (180 dias × 24), window 2025-07-05 00:00 → 2025-12-31 23:00 UTC.
- `symbol: BTCUSDT`, `source: binance_vision_spot`, `declared_gaps: []` (janela veio sem gaps detectados).
- Regenerável via `uv run python scripts/ingest_binance_vision.py --symbols BTCUSDT --timeframe 1h --start 2025-07-05 --end 2025-12-31`.

**`ethusdt_1h_20250705_20251231_binance_spot`** — segundo recorte real, mesmo script e mesma janela de BTC (transversalidade multi-asset, ADR-0009 §2-ter).
- 4320 barras 1h, window 2025-07-05 00:00 → 2025-12-31 23:00 UTC.
- `symbol: ETHUSDT`, `source: binance_vision_spot`, `declared_gaps: []`, `sha256: 91a039d9...`.

**`solusdt_1h_20250705_20251231_binance_spot`** — terceiro recorte real.
- 4320 barras 1h, window 2025-07-05 00:00 → 2025-12-31 23:00 UTC.
- `symbol: SOLUSDT`, `source: binance_vision_spot`, `declared_gaps: []`, `sha256: ee88d834...`.

## O que ainda não existe

Nenhum dos itens abaixo tem código correspondente. Eles vivem em `vision/` como alvo e não devem ser descritos aqui até existirem:

- Módulo `regimes` (classificação de regime).
- Módulo `validation` (walk-forward, monte carlo, stress).
- Módulo `ranking` (scoring multiobjetivo, reporting).
- Métricas além das quatro mínimas (`total_pnl`, `trade_count`, `hit_rate`, `max_drawdown`) — sem Sharpe, Sortino, profit factor, calmar, etc.
- Custos além dos três mínimos (sem maker/taker split, sem funding, sem impacto não-linear, sem tiers). Spread sintético estrutural já existe via ADR-0019.
- Stops / targets / filtros de volatilidade em qualquer estratégia (ADR-0011 §"Fica explicitamente fora", ADR-0013 §"Fica explicitamente fora").
- EMA/WMA ou qualquer MA adaptativa; grid de parâmetros; otimização de hiperparâmetros.
- Estratégias além de MA crossover, Donchian e dummy (RSI, ATR channel, etc.).
- Property-based de monotonicidade de custo para o modo `long_only=False` da Donchian (follow-up explícito da ADR-0013, ainda não implementado).
- Ordens além de market at next open (sem limit, sem stops).
- Múltiplas posições simultâneas; netting; portfolio-level risk.
- Integração com exchanges reais (ccxt deferred).
- `vectorbt` como engine (ADR-0001 manteve como direção macro; núcleo mínimo usa loop próprio).
