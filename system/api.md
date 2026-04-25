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
| `--spread-bps` | `0.0` | half-spread estrutural em bps aplicado contra o trader em cada fill (float ≥ 0, ADR-0019). Default zero preserva comportamento ADR-0006. |
| `--strategy` | `ma_crossover` | estratégia a executar. Opções: `ma_crossover` (ADR-0008, default), `donchian` (ADR-0011), `bollinger` (ADR-0026, mean-reversion long-only) e `dummy` (sanidade estrutural). |
| `--short-window` | `20` | janela curta da SMA do MA crossover (int > 0). Ignorado por outras estratégias. |
| `--long-window` | `50` | janela longa da SMA do MA crossover (int > short_window). Ignorado por outras estratégias. |
| `--long-only` / `--no-long-only` | `--long-only` | direcionalidade aplicável a `ma_crossover` (ADR-0012) **e** `donchian` (ADR-0013). Default preserva ADR-0008/ADR-0011 (cross-down/breakout bearish → `EXIT`). `--no-long-only` ativa modo simétrico: breakout/cross bearish → `ENTER_SHORT`; reversões resolvidas pelo engine com custo duplo. Ignorado por `dummy`. Em `bollinger`, `--no-long-only` é rejeitado com `NotImplementedError` (ADR-0026 §'Fica fora'). |
| `--entry-window` | `20` | janela de entrada do Donchian breakout (int > 0). Ignorado por outras estratégias. |
| `--exit-window` | `10` | janela de saída do Donchian breakout (int > 0). Ignorado por outras estratégias. |
| `--bollinger-window` | `20` | janela da média móvel da Bollinger band (int > 0, ADR-0026). Ignorado por outras estratégias. |
| `--bollinger-num-std` | `2.0` | número de desvios-padrão para a banda inferior (float > 0, ADR-0026). Ignorado por outras estratégias. |
| `--log-level` | `silent` | observabilidade operacional do engine. `silent` (default, nenhum log), `info` (duas linhas `backtest.start`/`backtest.end` em stderr), `debug` (inclui um evento por fill/rejection/trade/reverse-on-signal em stderr). Stream é stderr; stdout do summary permanece idêntico. |

Entry point: `alpha_forge.cli.app:main` (referenciado em `pyproject.toml`). Programaticamente: `from alpha_forge.cli.app import run; run(["run-demo", ...])`.

Exit codes: `0` em sucesso. Erros de validação pydantic ou integridade de dataset propagam exceção (não são engolidos).

### `alpha-forge validate` (ADR-0016)

Roda pipeline completo de `validation/` (walk-forward + Monte Carlo + cost_stress) sobre dataset + estratégia declarados, e persiste os artefatos em `results/validation/<run_id>/` via ADR-0015.

Flags compartilhadas com `run-demo` (idem defaults e semântica): `--dataset-id`, `--capital`, `--fracao`, `--alavancagem`, `--taker-fee-bps`, `--slippage-bps-per-notional`, `--spread-bps` (ADR-0019), `--strategy`, `--short-window`, `--long-window`, `--long-only`/`--no-long-only`, `--entry-window`, `--exit-window`, `--bollinger-window`, `--bollinger-num-std` (ADR-0026), `--log-level`.

Flags específicas:

| Flag | Default | Descrição |
|---|---|---|
| `--run-id` | **obrigatória** | string opaca; diretório `results/validation/<run_id>/` é criado/sobrescrito. Convenção de formato é do chamador (ADR-0015). |
| `--n-folds` | `5` | número de folds do walk-forward (int ≥ 2, ADR-0003). |
| `--scheme` | `rolling` | `rolling` ou `expanding` (ADR-0003). |
| `--train-fraction` | `0.5` | fração do tamanho do test_window usada como train em `rolling` (float ∈ (0,1)). |
| `--min-test-bars` | `50` | mínimo de barras por test_window (int ≥ 1). |
| `--mc-resamples` | `1000` | resamples do Monte Carlo (int ≥ 100, ADR-0003). |
| `--mc-seed` | `42` | semente do Monte Carlo; reprodutibilidade é contrato (ADR-0003). |
| `--stress label:fee_delta_bps:slip_delta_bps[:spread_delta_bps]` | `[]` | perturbação de custo, repetível (ADR-0014/ADR-0019). 3 partes (spread implícito = 0.0) OU 4 partes com spread explícito; ≤2 ou ≥5 partes rejeitados. Valores ≥ 0; pelo menos uma perturbação estritamente positiva em qualquer dos três componentes por spec; labels únicos. |
| `--skip-monte-carlo` | `False` | pula Monte Carlo; `monte_carlo.json` não é gravado. |
| `--skip-cost-stress` | `False` | pula cost_stress; `cost_stress.json` não é gravado. Ignora `--stress`. |

Comportamentos:

- Walk-forward roda sempre. `walk_forward.json` é sempre gravado.
- Monte Carlo agrega trades de todos os folds num `BacktestResult` sintético (mesmo padrão do integration test ADR-0015). Se nenhum fold gerou trades, MC é pulado silenciosamente com nota em stderr.
- Cost stress roda apenas se `--stress` não-vazio **e** `--skip-cost-stress` não for passado.
- Sobrescrita de artefatos pré-existentes em `results/validation/<run_id>/` é silenciosa (consistente com ADR-0015).
- Summary no stdout: uma linha por artefato persistido (caminho canônico, contagens). Contrato machine-parseable é o JSON persistido, não o stdout.

Exit codes: `0` em sucesso. `1` em `ValidationError` ou `DatasetIntegrityError` (erro operacional — mensagem curta em stderr). `2` em erro de flags (argparse). Exceções inesperadas sobem com stacktrace.

### `alpha-forge compare` (ADR-0018)

Compara duas corridas previamente persistidas (por `validate`), imprimindo diff humano read-only das quatro seções possíveis (`run_metadata`, `walk_forward`, `monte_carlo`, `cost_stress`).

Uso: `alpha-forge compare RUN_ID_A RUN_ID_B [--skip-run-metadata] [--skip-walk-forward] [--skip-monte-carlo] [--skip-cost-stress] [--log-level ...]`.

| Argumento/Flag | Default | Descrição |
|---|---|---|
| `RUN_ID_A` (posicional) | **obrigatório** | run_id da primeira corrida; resolvido via `validation_run_dir(run_id_a)`. |
| `RUN_ID_B` (posicional) | **obrigatório** | run_id da segunda corrida; resolvido via `validation_run_dir(run_id_b)`. |
| `--skip-run-metadata` | `False` | pula seção `run_metadata`. |
| `--skip-walk-forward` | `False` | pula seção `walk_forward`. |
| `--skip-monte-carlo` | `False` | pula seção `monte_carlo`. |
| `--skip-cost-stress` | `False` | pula seção `cost_stress`. |
| `--log-level` | `silent` | idem `run-demo`/`validate`. |

Comportamentos:

- **Read-only absoluto.** `compare` não grava, modifica ou apaga nenhum arquivo em `results/validation/<run_id>/`. Verificado em `tests/integration/test_cli_compare.py::test_compare_não_altera_artefatos` (tamanho + mtime dos 4 arquivos antes/depois).
- **Ausência assimétrica é primeira-classe.** Para `walk_forward`/`monte_carlo`/`cost_stress`, cada seção é tratada independentemente: ambos presentes → diff; só A → `"presente em A, ausente em B"`; só B → `"ausente em A, presente em B"`; nenhum → `"ausente em ambos"`. Checagem via `Path.exists()` no arquivo canônico.
- **`run.json` é sempre obrigatório.** Por ADR-0017, `run.json` é gravado antes do pipeline (mesmo em corridas que abortam). Sua ausência em qualquer lado é erro: `load_run_metadata` levanta `FileNotFoundError` que vira exit 1 com `"erro: ..."` em stderr. Sem checagem `exists()` preventiva.
- **Funções puras de diff.** Quatro helpers privados `_diff_run_metadata(a, b)`, `_diff_walk_forward(a, b)`, `_diff_monte_carlo(a, b)`, `_diff_cost_stress(a, b)` — assinatura `(T, T) -> list[str]`, sem I/O, testáveis unitariamente em `tests/unit/test_cli_compare_diffs.py`.
- **Formato de saída.** Header `run_a <id> (<path>)` + `run_b <id> (<path>)` + linha em branco; depois 4 blocos `--- <seção> ---` com linhas `  chave : a=<va>  b=<vb>  (tag)` ou `Δ=<sinal><valor>`. Δs numéricos usam `_fmt_delta` (4 casas, sinal explícito) para equity; 6 casas para `max_drawdown`; `.1f` para segundos de timestamp.
- **Walk-forward é agregado.** O diff mostra apenas 4 totais (`n_folds`, `total_trades`, `total_test_bars`, `sum_final_equity`) — diff fold-a-fold foi rejeitado para não poluir stdout (ADR-0018 §"Alternatives considered"). Para inspeção granular, carregue `load_walk_forward_folds` manualmente.
- **Monte Carlo compara percentis fixos.** Compara `n_resamples`, `seed`, os 5 percentis ADR-0003 (`5/25/50/75/95`), e os dois valores originais (`original_final_equity`, `original_max_drawdown`).
- **Cost stress indexa por `label`.** Cenários são pareados por `label` (chave natural estável da ADR-0014). Labels em união ordenada alfabeticamente; labels só em A → `"presente em A, ausente em B"` e vice-versa.
- **Divergência não é erro.** Exit 0 mesmo quando todo valor diverge — `compare` é leitura, não juiz. Política de "divergência = falha" viveria em `ranking/` (deferred).

Exit codes: `0` sempre em sucesso, mesmo divergente. `1` em run ausente (`FileNotFoundError` em `run.json`) ou `ValidationError` em algum `load_*` (mensagem curta em stderr). `2` em erro de flags (argparse). Não existe exit `≥3`.

### `alpha-forge rank` (ADR-0024)

Ordena N pilotos previamente validados por composite score, read-only sobre `results/validation/<slug>/`. Pré-requisito declarado do north star "testar centenas de estratégias e ranquear".

Uso: `alpha-forge rank [--runs-dir PATH] [--slug SLUG]* [--weights-file PATH] [--eligibility EXPR] [--agentic-dir PATH] [--output PATH] [--format json|table] [--log-level ...]`.

| Argumento/Flag | Default | Descrição |
|---|---|---|
| `--runs-dir` | `results/validation` | diretório raiz com subdirs por piloto; cada subdir precisa dos 4 JSONs canônicos. |
| `--slug` | (auto-discovery) | repetível; se vazio, roda sobre todos os subdirs completos de `--runs-dir`. |
| `--weights-file` | `DEFAULT_WEIGHTS` | TOML `[weights]`; chaves desconhecidas → erro; chaves ausentes → default. |
| `--eligibility` | `all` | v1 aceita `all` **ou** `release_decision (==\|!=) 'fail\|paper_only\|canary_only'`. Qualquer outra expressão → erro. |
| `--agentic-dir` | `<runs-dir>/../../agentic/active` | onde ler `<slug>/AUDIT.md` para parsear `release_decision`. |
| `--output` | `results/ranking/<generated_at>.json` | caminho final do leaderboard; diretório é criado. |
| `--format` | `json` | stdout como JSON indentado (default) ou `table` (markdown-ish). |

Comportamentos:

- **Score linear ponderado com min-max normalização.** 7 métricas normalizadas para `[0,1]` sobre a amostra atual (min-max; todos iguais → `0.5`), multiplicadas por pesos `ScoreWeights` e somadas. Documentado em ADR-0024 §"Score composto v1".
- **Pesos default** (ADR-0024): `w_fe=1.0, w_hit=2.0, w_mdd=1.5, w_stress=1.0, w_p5=1.5, w_fold_min=1.0, w_fold_std=0.5`. `w_hit` é o dobro dos outros porque o critério 1 primário da validação é `hit_rate`.
- **Tiebreak determinístico.** Score desc, slug asc — permutação-invariante.
- **Diretórios incompletos** (sem algum dos 4 JSONs, ou com schema violado) são **pulados com warning em stderr**; exit 0 continua. Exit 1 apenas se zero pilotos sobrevivem.
- **`spread_stress_ratio = fe(spread+10) / fe(baseline)`.** Piloto sem cenário `spread+10` é pulado (coerente com ADR-0019). `1.0` ≡ sem degradação; abaixo ≡ degrada.
- **`flags_digest`** = sha256 truncado (16 hex) sobre `json.dumps(flags, sort_keys=True)` — identidade invariante do piloto, resistente a renomeação de slug.
- **Leaderboard persistido com timestamp** via `save_leaderboard`; JSON indentado sem envelope (output de usuário, não artefato de engine).

Exit codes: `0` sucesso (inclusive com pilotos pulados por warning). `1` se zero pilotos elegíveis após filtros, ou `--weights-file` inválido. `2` em erro de flags (argparse).

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
- `CostModel` — pydantic `BaseModel`, frozen. Campos: `taker_fee_bps ≥ 0`, `slippage_bps_per_unit_notional ≥ 0` (ADR-0006), `spread_bps ≥ 0 default 0.0` (ADR-0019).
- `zero_cost() -> CostModel` — helper explícito para `CostModel(0.0, 0.0)` (spread herda default 0.0).
- `apply_cost(*, price_market: float, notional: float, capital_inicial: float, side: Side, is_entry: bool, cost_model: CostModel) -> float` — função pura. Ajusta preço **contra o trader**: entrada long / saída short pagam mais caro; saída long / entrada short recebem mais barato.

### Módulo `alpha_forge.backtest.lookahead_guard`
- `class LookaheadViolation(AssertionError)`
- `assert_causal(signals: pd.Series, prices: pd.Series) -> None`

### Módulo `alpha_forge.backtest.metrics`
- `compute_metrics(result: BacktestResult, capital_inicial: float) -> BacktestMetrics` — chamado obrigatoriamente pelo engine ao fim de `run_backtest`.

### Módulo `alpha_forge.backtest.engine`
- `class StrategyProtocol(Protocol)` — `decide(window: pd.DataFrame) -> Signal`.
- `run_backtest(*, prices: pd.DataFrame, strategy: StrategyProtocol, budget: RiskBudget, cost_model: CostModel, dataset_id: str, regime_filter: RegimeFilter | None = None) -> BacktestResult` — `cost_model` é **obrigatório** (ADR-0006); sem default silencioso. Use `zero_cost()` para rodar sem atrito. Implementa reverse-on-signal (ADR-0012): posição aberta + sinal de entrada na direção oposta → fecha e reabre em `t+1 open`, dois `Fill` com mesma `timestamp`, um `Trade` fechado, custo aplicado duas vezes. `regime_filter` opcional (ADR-0022): quando presente e `is_active(window)` retorna `False`, o engine coage `signal → HOLD` (flat) ou `EXIT` (posicionado) antes de consultar sizing/execução; `None` (default) preserva comportamento bit-a-bit pré-ADR-0022.
- `logger = logging.getLogger("alpha_forge.backtest")` — logger módulo-level (dev-only, não é contrato público). Emite em INFO: `backtest.start`, `backtest.end` (uma linha cada); em DEBUG: `engine.fill.open`, `engine.fill.close`, `engine.rejection`, `engine.reverse_on_signal` (uma linha por evento). Silencioso por padrão (sem handler configurado). CLI usa `--log-level` para habilitar.

### Módulo `alpha_forge.strategies.base`
- `class Strategy(ABC)` — `@abstractmethod decide(window: pd.DataFrame) -> Signal`.

### Módulo `alpha_forge.strategies.families.dummy`
- `DummyAlternatingStrategy` — implementação mínima do contrato `Strategy`. Disponível via `--strategy dummy` na CLI como ferramenta de sanidade.

### Módulo `alpha_forge.strategies.families.ma_crossover`
- `MovingAverageCrossoverStrategy(short_window: int, long_window: int, long_only: bool = True)` — primeira estratégia real (ADR-0008 + ADR-0012). SMA curta × SMA longa sobre `close`; stateless. Default `long_only=True` preserva ADR-0008 bit-a-bit; `long_only=False` ativa modo simétrico ADR-0012 (cross-down emite `ENTER_SHORT` em vez de `EXIT`; reversões são tratadas pelo engine). `__init__` valida: `TypeError` para não-inteiros em `short_window`/`long_window` (inclui `bool`); `TypeError` para `long_only` que não seja `bool` estrito (rejeita `int`, `None`, `str`); `ValueError` para `short_window <= 0`, `long_window <= 0`, ou `short_window >= long_window`. `decide(window) -> Signal` retorna `HOLD` durante warm-up (`len(window) < long_window + 1`) e nas barras sem cruzamento.

### Módulo `alpha_forge.strategies.families.bollinger`
- `BollingerMeanReversionStrategy(window: int, num_std: float, long_only: bool = True)` — terceira estratégia real (ADR-0026, mean-reversion long-only). Edge-triggered duplo: entrada `ENTER_LONG` quando `close[t-1] < mu_now - num_std·sigma_now` **e** `close[t-2] >= mu_prev - num_std·sigma_prev` (cruzou *para dentro* da banda inferior); saída `EXIT` quando `close[t-1] >= mu_now` **e** `close[t-2] < mu_prev` (cruzou a média de baixo para cima). `mu`/`sigma` (ddof=0) sobre `closes.iloc[:-1]` (barra `t` ignorada por construção). Arbitragem ordinal: EXIT antes de ENTER_LONG. `__init__` valida: `TypeError` para não-int em `window` (inclui `bool`), não-numérico em `num_std` (inclui `bool`), não-`bool` em `long_only`; `ValueError` para `window <= 0` ou `num_std <= 0`; **`NotImplementedError` para `long_only=False`** (ADR-0026 §'Fica fora': short side fica para ADR futura). `decide(window) -> Signal` retorna `HOLD` durante warm-up (`len(window) < window + 3`). Stateless: atributos públicos são apenas `window`, `num_std`, `long_only`.

### Módulo `alpha_forge.strategies.families.donchian`
- `DonchianBreakoutStrategy(entry_window: int, exit_window: int, long_only: bool = True)` — segunda estratégia real (ADR-0011 + ADR-0013). Breakout assimétrico em `high[t-1]` / `low[t-1]` sobre janelas independentes; stateless. Sem defaults no construtor para `entry_window`/`exit_window` (defaults 20/10 vivem só na CLI); `long_only=True` default preserva ADR-0011 bit-a-bit; `long_only=False` ativa modo simétrico ADR-0013 (breakout bearish emite `ENTER_SHORT` em vez de `EXIT`; reversões são tratadas pelo engine via reverse-on-signal ADR-0012). `__init__` valida: `TypeError` para não-inteiros em `entry_window`/`exit_window` (inclui `bool` e `float`); `TypeError` para `long_only` que não seja `bool` estrito (rejeita `int`, `None`, `str`); `ValueError` para `entry_window <= 0` ou `exit_window <= 0`. **Sem restrição de ordenação** entre as janelas (10/20, 20/10, 14/14 todos válidos). `decide(window) -> Signal` retorna `HOLD` durante warm-up (`len(window) < max(entry_window, exit_window) + 2`). No modo `long_only=True`: `EXIT` se bearish, `ENTER_LONG` se bullish; ambos simultâneos → `EXIT`. No modo `long_only=False`: `ENTER_SHORT` se bearish, `ENTER_LONG` se bullish; ambos simultâneos → `ENTER_SHORT` (arbitragem conservadora espelhada).

### Módulo `alpha_forge.regimes` (ADR-0022)
- `class RegimeFilter(Protocol)` — `name: str`; `is_active(window: pd.DataFrame) -> bool`. Contrato causal: filtro lê apenas `window.iloc[:-1]` (`iloc[-1]` é a barra `t` sendo decidida, ignorada por construção — ADR-0002 herdado).
- `SMASlopeFilter(window: int, min_slope_bps: float)` — implementação concreta. Ativa quando `abs(slope_bps) >= min_slope_bps`, onde `slope_bps = (sma[-1] - sma[-window]) / sma[-window] * 10000` (SMA sobre `close`). `min_slope_bps=0` aceita tudo. `__init__` valida: `TypeError` para não-inteiro em `window` (inclui `bool`), não-numérico em `min_slope_bps`; `ValueError` para `window <= 0` ou `min_slope_bps < 0`. Warm-up (`len(causal) < window + 1`) retorna `False`.
- `ATRRegimeFilter(window: int, min_atr_bps: float)` — segunda família (ADR-0022 extensão aditiva, sem nova ADR). Ativa quando `atr_bps >= min_atr_bps`, onde `atr = mean(TR[-window:])`, `TR[i] = max(high[i]-low[i], |high[i]-close[i-1]|, |low[i]-close[i-1]|)` (Wilder 1978 com média simples), `atr_bps = atr / close[-1] * 10000`. `min_atr_bps=0` aceita tudo. Valida `TypeError`/`ValueError` mesma forma que `SMASlopeFilter`. Warm-up (`len(causal) < window + 1`) retorna `False`.
- `BollingerWidthFilter(window: int, num_std: float, min_width_bps: float)` — terceira família (ADR-0022 extensão aditiva, sem nova ADR). Ativa quando `width_bps >= min_width_bps`, onde `ma = mean(close[-window:])`, `sigma = std(close[-window:], ddof=0)`, `width_bps = 2 * num_std * sigma / ma * 10000`. Captura volatilidade **estrutural** (spread entre bandas), ortogonal ao ATR (candle range). `min_width_bps=0` aceita tudo. Valida `TypeError` para não-int em `window` (inclui `bool`), não-numérico em `num_std`/`min_width_bps`; `ValueError` para `window <= 1`, `num_std <= 0`, `min_width_bps < 0`. Warm-up (`len(causal) < window`) retorna `False`.
- `TrendHTFRegimeFilter(htf: str, sma_window: int, mode: str)` — quarta família (ADR-0043); primeiro filtro com leitura HTF. Resample causal de `window.iloc[:-1]` para `htf` com `label="right", closed="right"` e `agg={open:first, high:max, low:min, close:last, volume:sum}`, descarta o último candle HTF resampled (anti-lookahead conservador — bucket potencialmente aberto), compara `close_htf[-1]` contra `sma(close_htf, sma_window)`. `mode="long_only"` ativa se `close_htf > sma`; `"short_only"` se `close_htf < sma`; `"both_sides"` se `close_htf != sma`. `htf` restrito a `{"4h", "1d", "1W"}`; `sma_window: int > 0` (rejeita `bool`/`float`). `ValueError` para `htf`/`mode` fora do conjunto permitido e `sma_window <= 0`; `TypeError` para tipos errados. Warm-up (`len(resampled_closed) < sma_window + 1`) retorna `False`. Index não-`DatetimeIndex` tenta coerção via `pd.to_datetime`; falha de coerção retorna `False`. Nota: `mode="short_only"` na API, reservado até strategies short-only existirem.
- `CompositeFilter(filters: Sequence[RegimeFilter], mode: Literal["and","or"])` — combinador lógico (ADR-0023). `mode="and"` → `all(f.is_active(w) for f in filters)`; `mode="or"` → `any(...)`. `__init__` valida: `mode` em {and, or}; `len(filters) >= 2`; sem aninhamento (filtros internos não podem ser `CompositeFilter`); sem duplicatas (dois filtros com mesmo `canonical_string` são rejeitados). Escopo inicial 1 nível — aninhamento (ADR-0024+) deferred.
- `canonical_string(regime_filter: RegimeFilter | None) -> str` — serializa para `run.json` (ADR-0017). `None → "none"`. `SMASlopeFilter → "sma_slope:min_slope_bps=<g>:window=<int>"`. `ATRRegimeFilter → "atr_regime:min_atr_bps=<g>:window=<int>"`. `BollingerWidthFilter → "bollinger_width:min_width_bps=<g>:num_std=<g>:window=<int>"`. `TrendHTFRegimeFilter → "trend_htf:htf=<str>:mode=<str>:sma_window=<int>"`. `CompositeFilter → "<mode>(<f1>,<f2>,...)"` com filtros internos ordenados lexicograficamente (ADR-0023 §comutatividade canônica). Ordem alfabética dos kwargs. Filtro desconhecido devolve apenas `name`.
- `parse_spec(spec: str) -> RegimeFilter | None` — parser da flag `--regime-filter` da CLI. `"none"` ou vazio → `None`. Três formas: (1) terminal `name:k=v:k=v` (ADR-0022); (2) composto `and(f1,f2,...)` ou `or(f1,f2,...)` (ADR-0023). Nomes terminais registrados: `sma_slope`, `atr_regime`, `bollinger_width`, `trend_htf` (ADR-0043). Levanta `ValueError` para nome desconhecido, kwarg duplicado, part sem `=`, kwargs obrigatórios ausentes, composição com `< 2` filtros, duplicatas em composição, ou aninhamento.

### Módulo `alpha_forge.validation` (ADR-0003)
- `walk_forward(*, prices, strategy, budget, cost_model, dataset_id, n_folds, scheme="rolling", train_fraction=0.5, min_test_bars=50, regime_filter: RegimeFilter | None = None) -> list[WalkForwardFold]` — divide o dataset em `n_folds` janelas de teste contíguas disjuntas; para cada fold com `train` anterior, executa `run_backtest` no `test_window`. Fold 0 é sempre pulado (sem train prévio). `scheme="rolling"` usa janela de treino proporcional a `train_fraction * test_size`; `scheme="expanding"` sempre desde o início. Causalidade herdada de `run_backtest` por construção. Sem tuning — estratégia é fixa por chamada. Levanta `ValidationError` para `n_folds < 2`, `train_fraction` fora de `(0,1)`, `scheme` inválido, ou dataset curto.
- `monte_carlo_trades(*, result, capital_inicial, n_resamples, seed) -> MonteCarloSummary` — reamostra com reposição a lista de PnLs de `result.trades`, recomputa curva de equity e `max_drawdown` em cada amostra. `seed: int` obrigatório (sem `None`) — reprodutibilidade bit-a-bit. Percentis fixos `{5, 25, 50, 75, 95}`. Levanta `ValidationError` para `n_resamples < 100`, `capital_inicial ≤ 0`, ou `result.trades` vazio. **Assume i.i.d. de PnL por trade** — variantes que respeitam autocorrelação (bootstrap em blocos) são deferred.
- Schemas: `WalkForwardWindow(start, end, bars)`, `WalkForwardFold(fold_index, train_window, test_window, result)`, `MonteCarloSummary(n_resamples, seed, final_equity_percentiles, max_drawdown_percentiles, original_final_equity, original_max_drawdown)` — todos frozen.
- `cost_stress(*, prices, strategy, budget, baseline_cost, perturbations, dataset_id, regime_filter: RegimeFilter | None = None) -> CostStressReport` (ADR-0014) — stress sistematizado de custos. Roda `run_backtest` uma vez por cenário (baseline + N perturbações), devolve tabela na ordem da lista. Perturbações são deltas **absolutos aditivos em bps** sobre os dois componentes de `CostModel`; não-negativos por contrato. Cada cenário perturbado recebe `dataset_id = f"{dataset_id}#stress{k}"`. Assert-a ADR-0010 por cenário antes de devolver (violação é bug, não flakiness). Levanta `ValidationError` para `perturbations` vazio, todo zero, ou com labels duplicados.
- Schemas adicionais (ADR-0014 + ADR-0019): `CostPerturbation(label, fee_delta_bps ≥ 0, slip_delta_bps ≥ 0, spread_delta_bps ≥ 0 default 0.0)`, `CostStressCell(scenario_index ≥ 0, label, cost, result, final_equity, final_equity_delta_vs_baseline)`, `CostStressReport(dataset_id, baseline, scenarios)` — todos frozen + `extra="forbid"`. Default de `spread_delta_bps` garante retrocompat de payloads JSON pré-E.9.
- Persistência (ADR-0015 + ADR-0017): `save_walk_forward_folds(*, folds, directory) -> Path`, `load_walk_forward_folds(*, directory) -> list[WalkForwardFold]`; `save_monte_carlo_summary(*, summary, directory) -> Path`, `load_monte_carlo_summary(*, directory) -> MonteCarloSummary`; `save_cost_stress_report(*, report, directory) -> Path`, `load_cost_stress_report(*, directory) -> CostStressReport`; `save_run_metadata(*, metadata, directory) -> Path`, `load_run_metadata(*, directory) -> RunMetadata`. Arquivos fixos `walk_forward.json` / `monte_carlo.json` / `cost_stress.json` / `run.json` dentro de `directory`. Envelope `{"schema_version": "1", "payload": ...}` — `schema_version` é **string**, não `int`. `load_*` levanta `ValidationError` para JSON malformado, envelope inválido, schema incompatível ou payload violando schema; `FileNotFoundError` para arquivo ausente. Sobrescrita permitida. Round-trip bit-a-bit (testado em `tests/unit/test_validation_persistence.py` e `tests/unit/test_run_metadata_persistence.py`).
- Schema de metadados (ADR-0017): `RunMetadata(alpha_forge_version: str min_length=1, timestamp_utc: datetime, command: str min_length=1, run_id: str min_length=1, flags: dict[str, str])` — frozen + `extra="forbid"`. `timestamp_utc` é timezone-aware UTC; `flags` coage todos os parâmetros argparse exceto `command` a string (listas via `repr`). Union heterogêneo em `flags` foi rejeitado na ADR-0017 §"Alternatives" para estabilidade de schema.
- `alpha_forge.io.paths.validation_run_dir(run_id: str) -> Path` (ADR-0015) — caminho canônico `results/validation/<run_id>/`. Não cria o diretório.

### Módulo `alpha_forge.ranking` (ADR-0024)
- `rank_pilots(*, slugs, runs_dir, weights=None, eligibility="all", agentic_dir=None, warn_stream=sys.stderr, generated_at=None) -> RankedLeaderboard` — consome `<runs_dir>/<slug>/{run,walk_forward,monte_carlo,cost_stress}.json` via loaders de `validation/persistence.py`. Score linear ponderado com min-max normalização sobre 7 métricas; tiebreak slug asc. Pilotos com artefatos ausentes/inválidos são pulados com warning em `warn_stream` (no fatal). Levanta `RankingError` apenas se zero pilotos sobrevivem à elegibilidade. `generated_at` opcional é seam para determinismo em testes.
- `discover_slugs(runs_dir: Path) -> list[str]` — retorna subdirs ordenados alfabeticamente que contêm os 4 JSONs canônicos; útil para auto-discovery no CLI.
- `load_weights_toml(path: Path) -> ScoreWeights` — lê TOML `[weights]`; chaves desconhecidas → `RankingError`; chaves ausentes → default documentado em ADR-0024.
- `save_leaderboard(leaderboard: RankedLeaderboard, path: Path) -> Path` — grava JSON indentado **sem envelope** (output de usuário, não artefato de engine).
- Schemas: `ScoreWeights(w_fe, w_hit, w_mdd, w_stress, w_p5, w_fold_min, w_fold_std)` com defaults `(1.0, 2.0, 1.5, 1.0, 1.5, 1.0, 0.5)`; `LeaderboardRow(rank ≥ 1, slug, fe_baseline, hit_baseline ∈ [0,1], mdd_baseline ∈ [0,1], trade_count ≥ 0, spread_stress_ratio, mc_p5, mc_p50, mc_p95, fold_max_hit, fold_min_hit, fold_std_hit ≥ 0, release_decision ∈ {fail, paper_only, canary_only}, composite_score, flags_digest len=16)`; `RankedLeaderboard(generated_at, alpha_forge_version, weights: dict[str, float], eligibility, rows)`. Todos frozen + `extra="forbid"`.
- Constante pública `DEFAULT_WEIGHTS: dict[str, float]` — único lugar onde os defaults estão declarados. Alterar aqui exige superseding ADR-0024.

### Módulo `alpha_forge.cli.app`
- `build_parser() -> argparse.ArgumentParser`
- `run(argv: Sequence[str] | None = None) -> int`
- `main() -> int`
- `parse_stress_specs(specs: Sequence[str]) -> list[CostPerturbation]` (ADR-0016 + ADR-0019) — parser público dos formatos `label:fee_delta_bps:slip_delta_bps` (3 partes) e `label:fee_delta_bps:slip_delta_bps:spread_delta_bps` (4 partes) da flag `--stress`. Reutilizável em testes e notebooks; levanta `ValueError` para specs malformadas (≤2 ou ≥5 partes), labels vazias/duplicadas e valores não-numéricos.
- `_now_utc() -> datetime` (ADR-0017) — seam de timestamp UTC timezone-aware, monkeypatch-ável em testes de CLI para fixar `RunMetadata.timestamp_utc`. Privado mas estável — testes de integração dependem do nome.

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
- **Ignora barra corrente por construção (ADR-0011):** `DonchianBreakoutStrategy.decide` lê `window["high"].iloc[:-1]` e `window["low"].iloc[:-1]` — a barra `t` (último elemento) é descartada antes de qualquer cálculo. Testado estruturalmente por `tests/unit/test_donchian_breakout.py::TestIgnoraBarraCorrente` e por property-based em `tests/property/test_donchian_causal.py` (mutação da barra `t` não altera o sinal).
- **Ignora barra corrente por construção (ADR-0026):** `BollingerMeanReversionStrategy.decide` lê `window["close"].iloc[:-1]` — a barra `t` é descartada antes do cálculo de `mu_now`/`sigma_now`/`mu_prev`/`sigma_prev`. Testado estruturalmente por `tests/unit/test_bollinger_mean_reversion.py::TestIgnoraBarraCorrente` e por property-based em `tests/property/test_bollinger_causal.py` (mutação de `OHLCV` em `t` ou em qualquer barra futura não altera o sinal).
- **Arbitragem de reversão (ADR-0011):** na raríssima barra em que `high[t-1]` rompe o máximo E `low[t-1]` rompe o mínimo, a estratégia emite `EXIT`. O engine, com posição aberta, fecha; sem posição, trata como no-op (fills permanecem coerentes com `position.side == FLAT`).
- **Reverse-on-signal (ADR-0012):** o engine é o único ponto que trata reversão de posição. Estratégias emitem um sinal por barra; sinal de entrada contra posição aberta dispara fechamento + abertura em `t+1 open`, com dois `Fill` de mesma `timestamp` e um `Trade` fechado. Regressão dura do caminho antigo testada em `tests/property/test_engine_reverse_on_signal.py`: em modo long-only (nunca entra na direção oposta), nenhum par de fills consecutivos compartilha `ts_exec`, e todo `Fill` de abertura é seguido por no máximo um `Fill` de fechamento (side=FLAT).
- **Observabilidade não altera contrato:** o logger `alpha_forge.backtest` é dev-only. Ligar/desligar logging não muda `BacktestResult` (testado em `tests/unit/test_engine_observability.py::TestLoggingNaoAlteraContrato`). Nome do namespace é estável; formato das mensagens **não é contrato público** (pode mudar sem ADR). Se virar consumido por `validation/`/`ranking/`, abrir ADR para cravar schema.
- **Walk-forward herda causalidade por composição (ADR-0003):** `validation.walk_forward` chama `run_backtest` por fold; cada fold recebe apenas sua fatia `test_window` e `assert_causal` continua sendo aplicada pelo engine. Testado por property-based em `tests/property/test_walk_forward_causal.py` (mutar barras de `test_window[k]` não altera `result[j]` para `j < k`).
- **Monte Carlo determinístico (ADR-0003):** mesma terna `(result, n_resamples, seed)` produz `MonteCarloSummary` bit-a-bit idêntico. Usa `numpy.random.default_rng(seed)`. Seed é `int` obrigatório (sem `None`).
- **Stress de custos respeita ADR-0010 por cenário (ADR-0014):** `cost_stress` assert-a `final_equity_delta_vs_baseline ≤ 1e-6 * capital_inicial` em cada `scenario_index ≥ 1` antes de devolver o relatório. Se qualquer cenário perturbado tiver `final_equity` acima do baseline além da tolerância, é bug do engine ou de `apply_cost`; `cost_stress` levanta `ValidationError` em vez de ocultar. Testado em `tests/unit/test_cost_stress.py::TestChamadaFeliz::test_monotonicidade_assertada_por_cenario` e reforçado estruturalmente em `tests/integration/test_cost_stress_pipeline.py` (perturbações ordenadas por custo crescente não aumentam `final_equity`).
- **Persistência de validação é round-trip bit-a-bit (ADR-0015):** `save_*` + `load_*` devolve um objeto pydantic `==` ao original — garantido estruturalmente por `model_dump(mode="json")` + `model_validate`, testado em `tests/unit/test_validation_persistence.py` e `tests/integration/test_validation_persistence_pipeline.py`. `schema_version` é parte do envelope JSON, **não** do objeto em memória; migração entre versões é ADR separada. Sobrescrita de arquivo é permitida (testes + CI gravam no mesmo diretório); proteção contra perda acidental vira ADR se for preciso.
- **Regime filter é causal + retrocompat bit-a-bit (ADR-0022):** `RegimeFilter.is_active(window)` lê apenas `window.iloc[:-1]` (barra `t` ignorada por construção, ADR-0002 herdado). Engine coage `is_active=False → HOLD` (flat) ou `EXIT` (posicionado) **antes** de consultar sizing/execução — filtro não cria nem fecha posições, apenas suprime sinais. `regime_filter=None` (default) percorre o caminho pré-ADR-0022 sem overhead. Um filtro sempre-ativo (`is_active == True`) é bit-a-bit idêntico a `regime_filter=None`. Testado em `tests/property/test_regime_filter_neutrality.py`, `test_regime_filter_lookahead.py`, `test_sma_slope_filter_monotonicity.py` (aumentar `min_slope_bps` nunca aumenta `trade_count`).
- **`run.json` é gravado antes do pipeline (ADR-0017):** na CLI `validate`, `save_run_metadata` é chamado antes de qualquer `run_backtest`. Consequência estrutural: corrida que aborta por `ValidationError`/`DatasetIntegrityError` no meio deixa `run.json` no diretório (trilha de auditoria), mas nenhum dos artefatos de pipeline. Testado em `tests/integration/test_cli_run_metadata.py::TestRunJsonSobreviveAbort`.

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

### `scripts/validate_artifacts.py` (ADR-0020)
Validador CLI dos artefatos agentic. Modo **opt-in**: se não há diretório `agentic/active/<slug>/` com pelo menos um sub-diretório, imprime `[validate_artifacts] nenhum piloto ativo — OK.` e sai com 0. Caso contrário, para cada piloto verifica presença e seções obrigatórias dos 6 artefatos (`SPEC.md` / `IMPLEMENTATION.md` / `VALIDATION.md` / `BACKTEST.md` / `AUDIT.md` / `CHECKLIST.md`) + `STATE.md` raiz; exit 1 se qualquer um está ausente, tem placeholders `{{...}}` não preenchidos, ou falta uma seção obrigatória. Mesma lógica do Stop hook `.claude/hooks/check_gates.py` — destinado a uso em CI local e por humanos.

Uso: `python scripts/validate_artifacts.py`.

## Overlay agentic (`.claude/`, `agentic/`) — ADR-0020

Infra de orquestração de pesquisa de estratégias. **Não toca `src/alpha_forge/`.** Composto por:

- **`.claude/settings.json`** — registro dos 3 hooks (`PreToolUse` → `block_live_trading.py`, `SessionStart` → `session_reminder.py`, `Stop` → `check_gates.py`) + `permissions.deny` para `rm -rf *`, `git push --force:*`, `LIVE_TRADING=true*`, edição de `.env*`/`*.pem`/`*.key`/`credentials*`.
- **`.claude/hooks/block_live_trading.py`** — PreToolUse guard: bloqueia `LIVE_TRADING=true`, edição de secrets, imports de venues reais (`ccxt`, `binance.client`, `.create_order`, etc.) em `src/`, endpoints de produção. `data.binance.vision` é exceção permitida.
- **`.claude/hooks/session_reminder.py`** — SessionStart reinjector das regras duras do laboratório (live desabilitado, promoção exige auditoria, secrets fora do repo).
- **`.claude/hooks/check_gates.py`** — Stop hook **opt-in**: só ativa se há piloto em `agentic/active/<slug>/`. Verifica presença/seções dos 6 artefatos + `STATE.md` raiz. Exit 2 + stderr se algo falta; exit 0 se nenhum piloto ativo.
- **`.claude/agents/*.md`** — 5 subagentes (`lead-orchestrator`, `strategy-researcher`, `strategy-implementer`, `backtest-validator`, `risk-auditor`). Leem o código+ADRs do projeto; escrevem artefatos em `agentic/active/<slug>/`.
- **`agentic/templates/*.md`** — 6 templates com `{{PLACEHOLDER}}` (SPEC/IMPLEMENTATION/VALIDATION/BACKTEST/AUDIT/CHECKLIST). Copiar para `agentic/active/<slug>/` ao abrir piloto.
- **`agentic/active/<slug>/`** — pilotos em andamento. Um sub-diretório por hipótese. `check_gates.py` e `validate_artifacts.py` cobram os artefatos.
- **`agentic/inactive/<slug>/`** — pilotos concluídos/arquivados (opcional, on-demand).

Fluxo: `lead-orchestrator` copia templates → `strategy-researcher` preenche `SPEC.md` → `strategy-implementer` traduz para código em `src/` → `backtest-validator` roda pipeline ADR-0016 e produz `VALIDATION.md`+`BACKTEST.md` → `risk-auditor` produz `AUDIT.md` com `release_decision ∈ {fail, paper_only, canary_only}` (nunca `live`). Ver [`agentic/README.md`](../agentic/README.md).

## Interfaces deferred (não expostas)

- Exchange connectors (`ccxt`) — não presente no código.
- `vectorbt` engine — não presente no código (`pyproject.toml` declara a dependência, mas nenhum `import vectorbt` existe em `src/`).
- Dashboards, HTTP API, agendadores — fora de escopo do produto.
