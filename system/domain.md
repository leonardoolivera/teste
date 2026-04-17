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

### `CostModel` (`backtest/cost.py`, ADR-0006)
Contrato de custos por execução de backtest. Frozen.
- `taker_fee_bps: float ≥ 0` — fee base em basis points.
- `slippage_bps_per_unit_notional: float ≥ 0` — slippage linear por unidade de `notional/capital_inicial`.
Helper `zero_cost()` devolve `CostModel(0.0, 0.0)` para uso explícito. Função pura `apply_cost(...)` aplica o ajuste **contra o trader** no preço (não no PnL): entrada long e saída short pagam preço mais caro; saída long e entrada short recebem preço mais barato.

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

### `MovingAverageCrossoverStrategy` (`strategies/families/ma_crossover/strategy.py`, ADR-0008)
Primeira estratégia real. **Long-only** nesta fase. Parâmetros: `short_window: int`, `long_window: int`, com `0 < short_window < long_window`. Validação cedo e explícita: `ValueError` para inteiros não positivos ou `short_window >= long_window`; `TypeError` para não-inteiros (inclui `bool`). SMA sobre coluna `close`.

Regra:
- `ENTER_LONG` se `short_ma[t] > long_ma[t]` **e** `short_ma[t-1] <= long_ma[t-1]`.
- `EXIT` se `short_ma[t] < long_ma[t]` **e** `short_ma[t-1] >= long_ma[t-1]`.
- Qualquer outro caso → `HOLD`. Empate exato não é sinal.
- Warm-up: `HOLD` enquanto `len(window) < long_window + 1`. Sem `fillna`, sem preenchimento mágico.

**Stateless.** `decide(window) -> Signal` é função pura de `window` e parâmetros. O engine é quem mantém o estado "em posição ou não"; a estratégia só emite intenção. `ENTER_LONG` com posição aberta vira no-op no engine; `EXIT` sem posição vira no-op.

### `DonchianBreakoutStrategy` (`strategies/families/donchian/strategy.py`, ADR-0011)
Segunda estratégia real. **Long-only** nesta fase. Parâmetros: `entry_window: int`, `exit_window: int`, ambos `> 0`. Validação cedo e explícita: `TypeError` para não-inteiros (inclui `bool`); `ValueError` para valores `<= 0`. `exit_window >= entry_window` é permitido (não é erro estrutural); só é arbitragem reversiva e o engine absorve.

Regra (todas as comparações usam `window.iloc[-2]` — a barra corrente `window.iloc[-1]` é ignorada por construção, reforçando ADR-0002):
- Canal de entrada: `entry_window_max = max(high[-entry_window-2 : -2])` (slice exclui `iloc[-1]` e a própria barra `t-1`).
- Canal de saída: `exit_window_min = min(low[-exit_window-2 : -2])`.
- `EXIT` se `low[t-1] < exit_window_min` (**verificação de saída antes da entrada** — prioridade ordenada).
- `ENTER_LONG` se `high[t-1] > entry_window_max`.
- Caso contrário → `HOLD`.
- Warm-up: `HOLD` enquanto `len(window) < max(entry_window, exit_window) + 2`.

**Stateless.** Pureza causal coberta por property-based em `tests/property/test_donchian_causal.py` (80 exemplos, mutação de OHLC completo da barra futura).

**Monotonicidade de custo:** coberta por property-based em `tests/property/test_donchian_cost_monotonicity.py` (ADR-0012, extensão de ADR-0010 à família Donchian). Invariante idêntica: `final_equity_high <= final_equity_low + 1e-6 * capital` quando `cost_high` domina `cost_low` componente a componente.

## CLI (`alpha_forge.cli`)

### `run-demo` (`cli/app.py`)
Subcomando único. Orquestra: `load_dataset` → `RiskBudget` → `CostModel` → estratégia (escolhida por `--strategy`, default `ma_crossover`) → `run_backtest` → `_print_summary`. Sem lógica de domínio escondida na CLI.

Flags: `--dataset-id`, `--capital`, `--fracao`, `--alavancagem`, `--taker-fee-bps`, `--slippage-bps-per-notional`, `--strategy {ma_crossover,dummy,donchian}`, `--short-window`, `--long-window` (MA crossover), `--entry-window`, `--exit-window` (Donchian).

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

**`btcusdt_1h_20251003_20251231_binance_spot`** — recorte curto para caracterização observacional (90 dias), ingerido em 2026-04-17.
- 2160 barras 1h (90 dias × 24), window 2025-10-03 00:00 → 2025-12-31 23:00 UTC.
- `symbol: BTCUSDT`, `source: binance_vision_spot`, `declared_gaps: []`.
- `sha256: 5db1a51578d430b8badc0097b03fceeb0eebfc077b0fb5fb65d3c309ecb9680d`.
- Usado apenas na seção observacional de [BACKTEST.md](../BACKTEST.md) (não é validação). Regenerável via `uv run python scripts/ingest_binance_vision.py --symbols BTCUSDT --timeframe 1h --start 2025-10-03 --end 2025-12-31`.

## Camada agentic (overlay, não substitui o protocolo `AGENTS.md`)

A camada agentic foi instalada como **overlay operacional** sobre o núcleo. Nenhum módulo em `src/` depende dela; é infraestrutura de orquestração e segurança. Detalhes contratuais em [README_AGENTIC_PILOT.md](../README_AGENTIC_PILOT.md).

### Subagentes (`.claude/agents/`)
Cinco subagentes Claude Code, cada um com frontmatter (name/description/tools/model) declarando escopo, ferramentas permitidas e modelo:
- `lead-orchestrator` (sonnet, effort high) — conduz o fluxo ponta a ponta; nunca avança sem gate verde; só delega.
- `strategy-researcher` (sonnet, effort high) — transforma hipótese em `SPEC.md` rigoroso.
- `strategy-implementer` (sonnet, effort high) — traduz `SPEC.md` em código; atualiza `IMPLEMENTATION.md`.
- `backtest-validator` (sonnet, effort xhigh) — roda testes + backtest + sensibilidade; produz `VALIDATION.md` e `BACKTEST.md`.
- `risk-auditor` (`claude-opus-4-7`, effort xhigh) — revisão adversarial; produz `AUDIT.md` com `release_decision`.

### Hooks determinísticos (`.claude/hooks/`)
Python stdlib-only, registrados em `.claude/settings.json`:
- `block_live_trading.py` (PreToolUse) — bloqueia `LIVE_TRADING=true`, edição de `.env`/secrets/chaves, imports de venues reais (`ccxt`, `binance.client`, `exchange.create_order`, `.execute_order`) em `src/`, URLs de endpoints de produção de trading (`api.binance.com`, `fapi.binance.com`, `api.bybit.com`, `api.okx.com`, etc.). Exceção explícita: `data.binance.vision` (histórico público).
- `session_reminder.py` (SessionStart) — reinjeta as 5 regras duras após compactação de contexto.
- `check_gates.py` (Stop) — verifica presença/coerência dos artefatos `SPEC.md|IMPLEMENTATION.md|VALIDATION.md|BACKTEST.md|AUDIT.md|CHECKLIST.md|STATE.md`; força continuação se incompleto.

### Artefatos por hipótese (raiz do repo)
Contratos rígidos, nomes fixos; um conjunto por hipótese ativa. Schema completo em [README_AGENTIC_PILOT.md](../README_AGENTIC_PILOT.md).
- `SPEC.md` — hipótese falsificável + contrato completo (mercado, timeframe, entradas/saídas, stops, sizing, fees, slippage, funding, condições inválidas, limitações).
- `IMPLEMENTATION.md` — arquivos alterados, mapeamento `SPEC → código`, decisões técnicas, gaps.
- `VALIDATION.md` — testes executados, conformidade por seção do `SPEC`, falhas conhecidas.
- `BACKTEST.md` — dataset, métricas, grid de sensibilidade, robustez, lookahead check.
- `AUDIT.md` — revisão adversarial, blockers, riscos operacionais, compliance, `release_decision`.
- `CHECKLIST.md` — gates ordenados: pesquisa → implementação → validação → auditoria → release.
- `ASSUMPTIONS.md` — suposições tomadas sem pedir ao usuário.

### Política de promoção entre estágios
Encadeamento hard, aplicado por hook + doutrina (CLAUDE.md §3):
`backtest_only` → (VALIDATION verde + BACKTEST robusto + AUDIT = `paper_only`) → `paper_only` → **IMPOSSÍVEL HOJE** → `live_trading`.

`live_trading` **nunca** sai deste repositório. Paper/live entra em repo separado, depois do núcleo maduro (`vision/02-scope.md` deferred).

### Scripts operacionais do overlay
- `scripts/validate_pilot.py` — grid de sensibilidade fees × slippage (4×4 por default) + checagem de monotonicidade + artefato JSON em `results/validation/<timestamp>_<strategy>.json`.
- `scripts/validate_artifacts.py` — checa presença/coerência dos artefatos agentic (usado no CI agentic).

### CI agentic (`.github/workflows/agentic.yml`)
Não-bloqueante (`continue-on-error: true`) por design. Roda: validação de artefatos + smoke backtest + grid de sensibilidade sobre sintético. O CI principal (`.github/workflows/ci.yml`) continua bloqueando merge.

## O que ainda não existe

Nenhum dos itens abaixo tem código correspondente. Eles vivem em `vision/` como alvo e não devem ser descritos aqui até existirem:

- Módulo `regimes` (classificação de regime).
- Módulo `validation` (walk-forward, monte carlo, stress).
- Módulo `ranking` (scoring multiobjetivo, reporting).
- Módulo `paper-trade` (deferred em `vision/02-scope.md`; sem ele, `paper_only` é estágio inexistente).
- Métricas além das quatro mínimas (`total_pnl`, `trade_count`, `hit_rate`, `max_drawdown`) — sem Sharpe, Sortino, profit factor, calmar, etc.
- Custos além do mínimo (sem maker, sem funding, sem bid-ask spread sintético, sem impacto não-linear, sem tiers).
- Short side em qualquer estratégia (tanto `MovingAverageCrossoverStrategy` quanto `DonchianBreakoutStrategy` são long-only nesta fase).
- EMA/WMA ou qualquer MA adaptativa; grid de parâmetros; otimização de hiperparâmetros.
- Estratégia não-MA/não-Donchian/não-dummy (RSI, mean-reversion estatística, etc.).
- Ordens além de market at next open (sem limit, sem stops explícitos — Donchian só tem saída por rompimento de canal).
- Equity guard / daily-loss limit / kill-switch em código (risco operacional R-2 do AUDIT; documentados em `vision/` mas não implementados).
- Múltiplas posições simultâneas; netting; portfolio-level risk.
- Integração com exchanges reais (ccxt deferred; bloqueado por hook).
- `vectorbt` como engine (ADR-0001 manteve como direção macro; núcleo mínimo usa loop próprio).
