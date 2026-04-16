# system/api.md

> **Layer:** Reality.
> **Purpose:** list endpoints/interfaces that **currently exist and work**.
> **Agent rule:** prefer auto-generation over hand-written tables.

---

## Sem API HTTP / GraphQL

Alpha Forge é biblioteca + CLI + notebooks, sem serviço web (confirmado em `vision/03-architecture.md`). As interfaces documentadas abaixo são a **API operacional interna** que o núcleo mínimo expõe aos demais módulos e ao usuário.

## CLI

### `alpha-forge run-demo`

Executa backtest mínimo sobre um dataset cadastrado.

| Flag | Default | Descrição |
|---|---|---|
| `--dataset-id` | `synthetic_btcusdt_1h_seed42` | id presente em `data/datasets.yaml`. |
| `--capital` | `10000.0` | capital inicial (float > 0). |
| `--fracao` | `0.1` | fração por trade (float ∈ (0, 1]). |
| `--alavancagem` | `2.0` | alavancagem máx (float ∈ [1, 10]). |
| `--taker-fee-bps` | `5.0` | taker fee em basis points (float ≥ 0). |
| `--slippage-bps-per-notional` | `2.0` | slippage linear por unidade de `notional/capital_inicial` (float ≥ 0). |
| `--strategy` | `ma_crossover` | estratégia a executar. Opções: `ma_crossover` (ADR-0008, default) e `dummy` (sanidade estrutural). |
| `--short-window` | `20` | janela curta da SMA do MA crossover (int > 0). Ignorado por outras estratégias. |
| `--long-window` | `50` | janela longa da SMA do MA crossover (int > short_window). Ignorado por outras estratégias. |

Entry point: `alpha_forge.cli.app:main` (referenciado em `pyproject.toml`). Programaticamente: `from alpha_forge.cli.app import run; run(["run-demo", ...])`.

Exit codes: `0` em sucesso. Erros de validação pydantic ou integridade de dataset propagam exceção (não são engolidos).

## API Python pública

### Módulo `alpha_forge`
- `__version__: str` — constante `"0.0.0"`.

### Módulo `alpha_forge.io.paths`
- `project_root() -> Path`
- `data_dir() -> Path`
- `data_raw_dir() -> Path`
- `data_processed_dir() -> Path`
- `datasets_manifest_path() -> Path`
- `processed_dataset_path(symbol: str, timeframe: str, dataset_id: str) -> Path`
- `results_dir() -> Path`
- `results_runs_dir() -> Path`

Nenhuma função cria diretórios; todas são puras (caminho deduzido).

### Módulo `alpha_forge.data.schemas`
- `OHLCVBar` — pydantic `BaseModel`, frozen.
- `GapRecord` — pydantic `BaseModel`, frozen.
- `DatasetManifest` — pydantic `BaseModel`, frozen.

### Módulo `alpha_forge.data.synthetic`
- `TIMEFRAME_DELTAS: dict[str, timedelta]` — constantes `1h`, `4h`, `1d`.
- `generate_ohlcv(*, start, periods, timeframe="1h", initial_price=100.0, drift=0.0002, volatility=0.01, seed=42) -> pd.DataFrame`.

### Módulo `alpha_forge.data.loaders`
- `class DatasetIntegrityError(RuntimeError)`
- `class DatasetNotFoundError(KeyError)`
- `load_manifest(manifest_path: Path | None = None) -> list[DatasetManifest]`
- `find_manifest_entry(dataset_id: str, manifest_path: Path | None = None) -> DatasetManifest`
- `sha256_of_file(path: Path) -> str`
- `load_dataset(dataset_id: str, manifest_path: Path | None = None) -> pd.DataFrame`

### Módulo `alpha_forge.risk.schemas`
- `RiskBudget` — pydantic `BaseModel`, frozen. Campos: `capital_inicial`, `fracao_por_trade`, `alavancagem_max`.

### Módulo `alpha_forge.risk.sizing`
- `fixed_fractional_position_sizing(budget: RiskBudget, preco_entrada: float, capital_corrente: float) -> float` — função pura. Nunca levanta; retorna `0.0`, `NaN` ou `±inf` em entradas patológicas. Engine decide rejeitar.

### Módulo `alpha_forge.backtest.schemas`
- `Side(StrEnum)` — `LONG`, `SHORT`, `FLAT`.
- `Signal(StrEnum)` — `ENTER_LONG`, `ENTER_SHORT`, `EXIT`, `HOLD`.
- `Fill` — frozen.
- `RejectionReason(StrEnum)` — `SIZE_ZERO`, `SIZE_NEGATIVE`, `SIZE_NAN`, `SIZE_INF`, `ABOVE_LEVERAGE_CAP`.
- `Rejection` — frozen.
- `Trade` — frozen. Par fechado (entrada, saída) com `pnl` pós-custo (ADR-0007).
- `BacktestMetrics` — frozen. Campos: `total_pnl`, `trade_count`, `hit_rate: float | None`, `max_drawdown` (ADR-0007).
- `BacktestResult` — inclui `trades: list[Trade]` e `metrics: BacktestMetrics | None`.

### Módulo `alpha_forge.backtest.cost`
- `CostModel` — pydantic `BaseModel`, frozen. Campos: `taker_fee_bps ≥ 0`, `slippage_bps_per_unit_notional ≥ 0` (ADR-0006).
- `zero_cost() -> CostModel` — helper explícito para `CostModel(0.0, 0.0)`.
- `apply_cost(*, price_market: float, notional: float, capital_inicial: float, side: Side, is_entry: bool, cost_model: CostModel) -> float` — função pura. Ajusta preço **contra o trader**: entrada long / saída short pagam mais caro; saída long / entrada short recebem mais barato.

### Módulo `alpha_forge.backtest.lookahead_guard`
- `class LookaheadViolation(AssertionError)`
- `assert_causal(signals: pd.Series, prices: pd.Series) -> None`

### Módulo `alpha_forge.backtest.metrics`
- `compute_metrics(result: BacktestResult, capital_inicial: float) -> BacktestMetrics` — chamado obrigatoriamente pelo engine ao fim de `run_backtest`.

### Módulo `alpha_forge.backtest.engine`
- `class StrategyProtocol(Protocol)` — `decide(window: pd.DataFrame) -> Signal`.
- `run_backtest(*, prices: pd.DataFrame, strategy: StrategyProtocol, budget: RiskBudget, cost_model: CostModel, dataset_id: str) -> BacktestResult` — `cost_model` é **obrigatório** (ADR-0006); sem default silencioso. Use `zero_cost()` para rodar sem atrito.

### Módulo `alpha_forge.strategies.base`
- `class Strategy(ABC)` — `@abstractmethod decide(window: pd.DataFrame) -> Signal`.

### Módulo `alpha_forge.strategies.families.dummy`
- `DummyAlternatingStrategy` — implementação mínima do contrato `Strategy`. Disponível via `--strategy dummy` na CLI como ferramenta de sanidade.

### Módulo `alpha_forge.strategies.families.ma_crossover`
- `MovingAverageCrossoverStrategy(short_window: int, long_window: int)` — primeira estratégia real (ADR-0008). SMA curta × SMA longa sobre `close`; long-only; stateless. `__init__` valida: `TypeError` para não-inteiros (inclui `bool`); `ValueError` para `short_window <= 0`, `long_window <= 0`, ou `short_window >= long_window`. `decide(window) -> Signal` retorna `HOLD` durante warm-up (`len(window) < long_window + 1`) e nas barras sem cruzamento.

### Módulo `alpha_forge.cli.app`
- `build_parser() -> argparse.ArgumentParser`
- `run(argv: Sequence[str] | None = None) -> int`
- `main() -> int`

## Invariantes de contrato (aplicadas estruturalmente, não por convenção)

- **Causalidade (ADR-0002):** `run_backtest` só entrega `prices[:t+1]` à estratégia e chama `assert_causal` ao fim. Estratégia não tem acesso ao DataFrame completo por design.
- **Execução `t+1 open` (ADR-0002):** todo `Fill` satisfaz `fill.timestamp > fill.signal_timestamp`. Testado em integration.
- **Hard cap de alavancagem (ADR-0004):** `RiskBudget(alavancagem_max=10.1)` falha na validação pydantic antes de chegar ao engine.
- **Rejeição determinística (ADR-0004):** sizing inválido nunca vira trade. `Rejection` é gravada com motivo categorizado.
- **Imutabilidade do manifesto (ADR-0005):** `load_dataset` recusa arquivo cujo sha256 diverge do registrado; muda conteúdo → muda `dataset_id`.
- **Gaps declarados (ADR-0005):** continuidade temporal é checada no loader contra `declared_gaps`; gap não declarado bloqueia carregamento.
- **Custo contra o trader (ADR-0006):** `apply_cost` ajusta o preço de execução, nunca o PnL; entrada e saída pagam atrito independente. `run_backtest` exige `cost_model` explícito.
- **Métricas obrigatórias (ADR-0007):** `run_backtest` preenche `result.metrics` no fim; `hit_rate` é `None` quando `trade_count == 0` (nunca `0.0` nem `NaN`). Posição aberta no fim entra via `final_equity`, não como `Trade`.
- **Validação cedo e explícita da estratégia (ADR-0008):** `MovingAverageCrossoverStrategy.__init__` falha com `TypeError` para não-inteiros e `ValueError` para inteiros fora de faixa. Sem corrigir silenciosamente.
- **Pureza causal da estratégia (ADR-0008):** `decide(window) -> Signal` é função de `window` e parâmetros. Estado interno mínimo; não mantém "em posição ou não" — essa responsabilidade é do engine. Testado por property-based em `tests/property/test_ma_crossover_causal.py`: mutar barra futura nunca altera sinal em `t`.

## Scripts operacionais (fora de `src/`)

### `scripts/bootstrap_synthetic_dataset.py`
Gera o dataset seminal `synthetic_btcusdt_1h_seed42` e grava no manifesto. Determinístico.

### `scripts/ingest_binance_vision.py` (ADR-0009)
Ingesta klines mensais públicas de Binance Vision para qualquer símbolo/timeframe. Multi-símbolo desde o dia 1; nenhum ramo especial por ativo. Código de rede (download HTTPS + unzip) mora **apenas aqui** — `src/` não importa nada de rede.

Flags:
- `--symbols` — lista separada por vírgula (ex: `BTCUSDT,ETHUSDT,SOLUSDT`).
- `--timeframe` — ex: `1h`, `4h`, `1d`.
- `--start`, `--end` — `YYYY-MM-DD` ou ISO8601 em UTC; `end` só com data vira 23:59:59.
- `--declared-gap START,END[,REASON]` — repetível; gap declarado explicitamente.

Símbolo canônico único: normaliza (`upper`, sem `/`, `-`, `_`, espaço) na entrada. Manifesto, Parquet path e URL de Binance usam a mesma forma. Gaps detectados mas não declarados rejeitam a ingestão sem deixar Parquet órfão; operador declara via `--declared-gap` e re-roda.

Resumo impresso por símbolo: `symbol`, `timeframe`, `window`, `bars_saved`, `gaps_detected`, `dataset_id`, `sha256`, `status`, `note`.

## Interfaces deferred (não expostas)

- Exchange connectors (`ccxt`) — não presente no código.
- `vectorbt` engine — não presente no código (`pyproject.toml` declara a dependência, mas nenhum `import vectorbt` existe em `src/`).
- Dashboards, HTTP API, agendadores — fora de escopo do produto.
