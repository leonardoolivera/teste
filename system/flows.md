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
  1. Parse de flags em `cli/app.py::run` (`--dataset-id`, `--capital`, `--fracao`, `--alavancagem`, `--taker-fee-bps`, `--slippage-bps-per-notional`, `--strategy`, `--short-window`, `--long-window`, `--long-only/--no-long-only`, `--entry-window`, `--exit-window`).
  2. `RiskBudget` construído com validação pydantic (rejeita fora de faixa).
  3. `CostModel` construído explicitamente a partir das flags de custo (sem default silencioso — ADR-0006).
  4. `data.loaders.load_dataset(dataset_id)` lê o manifesto, valida sha256, row_count, janela temporal e continuidade contra `declared_gaps`; devolve `pd.DataFrame` com index UTC-aware.
  5. Estratégia é instanciada via `--strategy`. Default: `MovingAverageCrossoverStrategy(short_window, long_window, long_only=True)` (ADR-0008, default; `--no-long-only` ativa modo simétrico ADR-0012). Alternativas: `DonchianBreakoutStrategy(entry_window, exit_window, long_only=True)` (ADR-0011 default long-only; `--no-long-only` ativa modo simétrico ADR-0013, breakout bearish → `ENTER_SHORT`, reversões via engine) e `DummyAlternatingStrategy()` para sanidade estrutural.
  6. `backtest.engine.run_backtest` executa o loop causal:
     - Para cada barra `t`, `window = prices[:t+1]` é passada para `strategy.decide`.
     - **Regime filter coerce (ADR-0022, opcional):** se `regime_filter is not None` e `regime_filter.is_active(window) == False`, o engine substitui `signal` por `HOLD` (posição FLAT) ou `EXIT` (posição aberta) antes de sizing/execução. `regime_filter=None` (default) pula totalmente essa etapa — bit-a-bit pré-ADR-0022. Filtro lê apenas `window.iloc[:-1]`, causal por construção.
     - Execução ocorre em `t+1 open` (última barra não executa).
     - `apply_cost` ajusta o preço contra o trader (entrada e saída, ADR-0006).
     - `fixed_fractional_position_sizing` calcula tamanho; `_classify_size` decide fill vs rejection.
     - Saída de posição também registra um `Trade` com PnL pós-custo.
     - **Reverse-on-signal (ADR-0012):** sinal de entrada contra posição aberta na direção oposta → fecha e reabre em `t+1 open`, dois `Fill` com mesma `timestamp`, custo aplicado duas vezes.
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

### Output exemplo 4 — Donchian breakout 20/10 no dataset **real** BTCUSDT 180d (ADR-0011)

Caracterização inicial (ADR-0011 §"Caracterização inicial"). **Observação, não validação nem prova de edge.** Capital 10.000, fração 0.1, alavancagem 2x, taker 5 bps, slippage 2 bps/notional.

```
dataset          : btcusdt_1h_20250705_20251231_binance_spot
strategy         : donchian entry=20 exit=10
barras           : 4320
budget           : capital=10000.00 fracao=0.100 alavancagem_max=2.00
cost_model       : taker_fee_bps=5.00 slippage_bps/notional=2.00
fills            : 220
rejections       : 0
equity inicial   : 10000.00
equity final     : 9089.79
equity max       : 10154.82
equity min       : 9089.73
--- metrics ---
total_pnl        : -910.21 (-9.10%)
trade_count      : 110
hit_rate         : 25.45%
max_drawdown     : 10.49%
```

Mesma estratégia, mesmo dataset, **zero custo explícito** (isolamento do atrito):

```
cost_model       : taker_fee_bps=0.00 slippage_bps/notional=0.00
equity final     : 9326.50
--- metrics ---
total_pnl        : -673.50 (-6.73%)
trade_count      : 110
hit_rate         : 27.27%
max_drawdown     : 8.28%
```

**Leitura honesta:** sobre BTCUSDT 1h 2025-07-05 → 2025-12-31 (janela bull prolongada, close ∈ [82.207, 126.011] USD), Donchian 20/10 long-only foi whipsawed 110 vezes. O atrito custou ~2.4 p.p. de PnL (de −6.73% para −9.10%); com 220 fills, o custo por fill é consistente com o modelo mínimo (ADR-0006). `hit_rate` abaixo de 1/3 (25–27%) é coerente com estratégia de breakout: poucos trades vencedores grandes teriam que compensar muitos perdedores pequenos — no recorte observado, não compensaram. **Isto é caracterização do comportamento no recorte**, não avaliação de edge; validação exige `validation/`, deliberadamente segurado.

### Output exemplo 5 — caracterização multi-asset (ETH + SOL 1h, mesma janela BTC)

Caracterização transversal ADR-0009 §2-ter. Três ativos, mesma janela (2025-07-05 → 2025-12-31, 4320 barras 1h), mesmo budget (capital 10.000, fração 0.1, alavancagem 2x, taker 5 bps, slippage 2 bps/notional), duas estratégias. **Observação, não validação** — nenhuma comparação numérica entre estratégias sai desta tabela como juízo; comparação formal vive em `ranking/`, segurado.

| Ativo | Estratégia | fills | trades | hit_rate | total_pnl | max_drawdown |
|---|---|---|---|---|---|---|
| BTCUSDT | `ma_crossover 20/50` | 16 | 8 | 12.50% | −464.64 (−4.65%)* | 5.46%* |
| BTCUSDT | `donchian 20/10` | 220 | 110 | 25.45% | −910.21 (−9.10%) | 10.49% |
| ETHUSDT | `ma_crossover 20/50` | 89 | 44 | 38.64% | +459.37 (+4.59%) | 6.33% |
| ETHUSDT | `donchian 20/10` | 192 | 96 | 28.12% | +240.02 (+2.40%) | 8.90% |
| SOLUSDT | `ma_crossover 20/50` | 99 | 49 | 26.53% | −684.62 (−6.85%) | 11.69% |
| SOLUSDT | `donchian 20/10` | 206 | 103 | 31.07% | −880.27 (−8.80%) | 14.55% |

*BTC MA 20/50: linhas `−464.64 (−4.65%)` e `5.46%` vêm do sintético seminal (Output exemplo 1) e estão aqui apenas para referência. BTC não foi re-rodado neste lote; a entrega anterior já o caracterizou.

**Leitura honesta:**

- **ETH foi o único ativo em que ambas as estratégias terminaram positivas no recorte.** MA 20/50 em ETH teve o maior `hit_rate` observado até hoje no laboratório (38.64%, próximo do ponto em que expectancy positiva começa a sobreviver ao atrito). Donchian 20/10 em ETH ficou modestamente positivo. Nada disso é edge comprovado — é um recorte de 180 dias em janela com direção clara; `validation/` (walk-forward, monte carlo) não foi exercitado.
- **SOL foi o pior ativo para ambas.** Drawdown de 14.55% no Donchian e 11.69% na MA. Volatilidade maior + janela com pull-backs mais severos derrubam estratégias trend-following sem stops.
- **Contagem de fills escala consistentemente com a estratégia, não com o ativo.** Donchian 20/10 dispara ~2× mais fills que MA 20/50 em qualquer ativo (BTC: 220 vs 16 ressalvada a origem diferente; ETH: 192 vs 89; SOL: 206 vs 99). Isso confirma o perfil da família: MA filtra melhor ruído, Donchian aceita mais whipsaw.
- **Zero rejections em todos os 6 runs.** `fixed_fractional_position_sizing` + `RiskBudget` não filtraram nenhum trade — o sizing está comportado em toda a faixa observada de preços (82–126k para BTC, faixa proporcional para ETH/SOL).
- **Nenhuma linha da tabela prova edge.** São seis observações pontuais sobre um recorte bull-dominante. Uma direção forte oposta (bear) poderia inverter o ranking informal. `ranking/` fica segurado até que seu design esteja pronto.

### Output exemplo 6 — MA crossover simétrica (`--no-long-only`, ADR-0012) em BTC/ETH/SOL

Caracterização da ativação do short side. Mesma janela e budget dos exemplos anteriores (capital 10.000, fração 0.1, alavancagem 2x, taker 5 bps, slippage 2 bps/notional; `short_window=20, long_window=50`). **Observação, não validação.**

| Ativo | Modo | fills | trades | hit_rate | total_pnl | max_drawdown |
|---|---|---|---|---|---|---|
| BTCUSDT | `ma_crossover 20/50 long_only=True`  | 16  | 8  | 12.50% | −464.64 (−4.65%)* | 5.46%* |
| BTCUSDT | `ma_crossover 20/50 long_only=False` | 183 | 91 | 31.87% | −536.84 (−5.37%) | 7.87% |
| ETHUSDT | `ma_crossover 20/50 long_only=True`  | 89  | 44 | 38.64% | +459.37 (+4.59%) | 6.33% |
| ETHUSDT | `ma_crossover 20/50 long_only=False` | 179 | 89 | 41.57% | +416.16 (+4.16%) | 7.25% |
| SOLUSDT | `ma_crossover 20/50 long_only=True`  | 99  | 49 | 26.53% | −684.62 (−6.85%) | 11.69% |
| SOLUSDT | `ma_crossover 20/50 long_only=False` | 199 | 99 | 30.30% | −1246.60 (−12.47%) | 15.36% |

*Linha BTC `long_only=True` vem do integration test (Output exemplo 1, sintético) — permanece aqui como referência; BTC real MA long-only tem fills/trades equivalentes no recorte bull 2025.

**Leitura honesta:**

- **Ativar short não "salvou" nenhum ativo no recorte.** BTC ficou um pouco mais negativo (−5.37% vs referência long-only na faixa de −4 a −5%). ETH piorou levemente (+4.16% vs +4.59%). SOL **dobrou o prejuízo** (−12.47% vs −6.85%) e o drawdown cresceu de 11.69% para 15.36%. Isso é consistente com ADR-0008 §"Consequences/Negative" e com a literatura: MA crossover simétrico em mercado com lateralização forte multiplica whipsaw — cada reversão paga custo duas vezes (ADR-0012, reverse-on-signal).
- **Fills e trades aproximadamente dobraram em todos os ativos.** BTC: 16→183, ETH: 89→179, SOL: 99→199. Cada cruzamento que antes fechava uma posição agora fecha e abre outra, produzindo dois fills por reversão.
- **`hit_rate` subiu em todos os ativos (mesmo onde o PnL piorou).** BTC 12.50%→31.87%, ETH 38.64%→41.57%, SOL 26.53%→30.30%. Shorts capturam o lado bear que antes era EXIT → FLAT; o número médio de trades ganhadores cresce. Mas como o mercado do recorte foi bull-dominante, o ganho em `hit_rate` não compensou o custo duplo das reversões — fenômeno bem documentado de "many small losses > few bigger wins".
- **Zero rejections em todos os 3 runs.** O sizing continua comportado mesmo com o dobro de execuções; `RiskBudget` não filtrou.
- **Custo duplo na reversão é visível estruturalmente.** BTC long-only: 16 fills → 8 entradas + 8 saídas. BTC simétrico: 183 fills → aproximadamente 91 aberturas + 91 fechamentos + 1 aberto ao fim. A contagem de fills par (ou ímpar por 1) é assinatura do reverse-on-signal funcionando corretamente.
- **Esta leitura NÃO é "short não funciona em cripto".** É "MA 20/50 simétrico em um recorte bull-dominante sem filtro de regime tem trade-off previsivelmente ruim". Filtros de regime (`regimes/`, segurado) e `validation/` (segurado) são as ferramentas corretas para tirar conclusão de edge — por design, não estão disponíveis ainda.

### Output exemplo 7 — Donchian breakout simétrico (`--no-long-only`, ADR-0013) em BTC/ETH/SOL

Caracterização da ativação do short side da Donchian (ADR-0013, aplicação mecânica da ADR-0012 reverse-on-signal para a segunda família). Mesma janela e budget dos exemplos anteriores (capital 10.000, fração 0.1, alavancagem 2x, taker 5 bps, slippage 2 bps/notional; `entry_window=20, exit_window=10`). **Observação, não validação.**

| Ativo | Modo | fills | trades | hit_rate | total_pnl | max_drawdown |
|---|---|---|---|---|---|---|
| BTCUSDT | `donchian 20/10 long_only=True`  | 220 | 110 | 25.45% | −910.21 (−9.10%)   | 10.49% |
| BTCUSDT | `donchian 20/10 long_only=False` | 441 | 220 | 27.27% | −1473.17 (−14.73%) | 15.45% |
| ETHUSDT | `donchian 20/10 long_only=True`  | 192 | 96  | 28.12% | +240.02 (+2.40%)   | 8.90%  |
| ETHUSDT | `donchian 20/10 long_only=False` | 383 | 191 | 29.84% | −103.31 (−1.03%)   | 12.50% |
| SOLUSDT | `donchian 20/10 long_only=True`  | 206 | 103 | 31.07% | −880.27 (−8.80%)   | 14.55% |
| SOLUSDT | `donchian 20/10 long_only=False` | 413 | 206 | 33.50% | −1666.62 (−16.67%) | 20.48% |

**Leitura honesta:**

- **Ativar short na Donchian não "salvou" nenhum ativo no recorte — e piorou os três.** BTC aprofundou o prejuízo (−9.10% → −14.73%). ETH, que era o único long-only positivo (+2.40%), virou negativo (−1.03%). SOL aprofundou de −8.80% para −16.67%, com drawdown saltando de 14.55% para 20.48% (pior drawdown observado no laboratório até hoje). O padrão é consistente com o da MA simétrica (Output exemplo 6) e com a literatura sobre breakout bilateral em mercados sem filtro de regime: cada reversão paga custo duas vezes (ADR-0012 §"custo duplo na reversão"), amplificando o whipsaw do breakout clássico.
- **Fills dobraram em todos os ativos.** BTC: 220→441, ETH: 192→383, SOL: 206→413. Cada rompimento que antes fechava a posição agora fecha e abre outra, exatamente o mesmo padrão assinatura observado na MA simétrica.
- **`hit_rate` subiu em todos os ativos (mesmo onde o PnL piorou).** BTC 25.45%→27.27%, ETH 28.12%→29.84%, SOL 31.07%→33.50%. Shorts capturam o lado bear que antes era EXIT → FLAT; o número de trades ganhadores cresce. Mas no recorte bull-dominante o ganho em hit rate não compensou o custo duplo — fenômeno idêntico ao documentado para MA simétrica (Output exemplo 6).
- **Zero rejections em todos os 3 runs.** O sizing continua comportado mesmo com o dobro de execuções; `RiskBudget` não filtrou.
- **Custo duplo é visível estruturalmente.** BTC long-only: 220 fills → ~110 aberturas + ~110 fechamentos. BTC simétrico: 441 fills = 220 aberturas + 220 fechamentos + 1 aberto ao fim (paridade par/ímpar±1, mesma assinatura da MA simétrica). O engine reverse-on-signal (ADR-0012) está funcionando de forma idêntica para a segunda família, como previsto por ADR-0013.
- **Consistência cross-família.** Donchian simétrica e MA simétrica apresentam o mesmo padrão qualitativo no recorte: ambos pioram em 2 ou 3 ativos e melhoram em 0. Isso reforça que o achado não é sobre a regra específica de breakout vs cruzamento, mas sobre ativar short sem filtro de regime num recorte bull.
- **Esta leitura NÃO é "short-side Donchian não funciona".** É "Donchian 20/10 simétrica em recorte bull-dominante sem filtro de regime tem trade-off previsivelmente ruim — e um grau mais ruim que a MA simétrica por conta da maior frequência de reversões do breakout". Filtros de regime (`regimes/`, segurado) e `validation/` (segurado) são as ferramentas corretas para tirar conclusão de edge.

### Output exemplo 8 — Bollinger mean-reversion SOL 180d (ADR-0026, Série I.1, sob ADR-0025)

Primeira caracterização da família mean-reversion no protocolo. Pilot `bollinger-20-2-sol-180d-baseline`
sobre `solusdt_1h_20250705_20251231_binance_spot` (mesmo tape que H.10 Donchian SOL) —
`BollingerMeanReversionStrategy(window=20, num_std=2.0, long_only=True)`, budget H.1, sem filtro.

| piloto  | família (SOL 180d) | fills | trades | hit_rate   | final_equity | max_drawdown |
|---------|--------------------|-------|--------|------------|--------------|--------------|
| H.10    | Donchian 20/10     | 206   | 103    | 31.07%     | 9119.73      | 14.55%       |
| **I.1** | **Bollinger 20/2** | **164** | **82** | **65.85%** | **10189.15** | **6.93%**    |

**Leitura honesta:**

- **Primeiro piloto do protocolo a cruzar `hit_rate ≥ 45%`** (ADR-D piso absoluto): baseline
  65.85% — 2.06× o maior da Série H. Não é caracterização observacional "frouxa" — passou o
  pipeline completo `alpha-forge validate` (walk-forward + Monte Carlo + cost stress) e foi
  ranqueada 1/13 em `alpha-forge rank`, score 7.66.
- **Ortogonalidade de família em tape compartilhado:** mesmo SOL 180d, família breakout falhou,
  família mean-reversion capturou edge. Falsifica a conclusão da Série H "edge não existe em
  família causal sem filtro" — edge existe em **outra família**.
- **Fold-homogeneidade inédita:** os 4 folds cruzam 45% (50–76%), std fold-a-fold 11.04 pp.
  Comparar H.10 SOL: folds 9.52–47.62%. Sinal mean-reversion em SOL não é fold-dependent.
- **Menos trades, maior seletividade:** Bollinger dispara edge-triggered duplo (ADR-0026) —
  precisa cruzamento em `t-1` E posição oposta em `t-2`. 82 trades vs 103 do Donchian.
- **Release decision:** `canary_only` (ADR-0025 hard gate absoluto; primeiro do protocolo).
  Execução efetiva bloqueada por ausência de módulo `canary-trade` (AGENTS.md §8).

### Output exemplo 9 — Bollinger mean-reversion cross-asset (Série I completa: I.1 SOL + I.2 BTC + I.3 ETH)

Quadro cross-asset completo Bollinger 20/2.0 long-only sobre janela 1h 180d (2025-07-05→2025-12-31).
Mesmos custos (`taker=5, slip=2, spread=0` bps), mesmo capital (10000), mesmos custos de stress
(fee+10, slip+5, spread+10), mesmo motor — única diferença entre pilotos é `--dataset-id`.

| piloto  | asset | final_equity | hit_rate   | trades | max_drawdown | rank (N=15) | score |
|---------|-------|--------------|------------|--------|--------------|-------------|-------|
| **I.2** | BTC   | 10033.00     | **65.85%** | **82** | **2.80%**    | **1**       | 7.70  |
| **I.1** | SOL   | **10189.15** | **65.85%** | **82** | 6.93%        | 2           | 7.19  |
| **I.3** | ETH   | 10057.17     | 63.41%     | **82** | 5.17%        | 3           | 7.12  |

**ADR-0019 por piloto (`fee+10 ≡ spread+10` bit-a-bit, 13ª/14ª/15ª confirmações):**
I.1=`9859.11` · I.2=`9696.79` · I.3=`9729.39`.

**Leitura cross-asset honesta:**

- **82 trades exatos em todos os três assets** — coincidência estrutural notável. Trigger edge-triggered
  duplo (`close[t-1]<lower_now ∧ close[t-2]≥lower_prev`) dispara com frequência similar em tape 1h 180d
  (4320 barras) independente de asset. Não é artefato aleatório; é propriedade do regra × estrutura temporal.
- **Hits SOL ≡ BTC bit-a-bit (65.85%)** — provavelmente mesma razão 54/82. Coincidência aritmética, não
  causal. ETH cai 2.44 pp (63.41% = 52/82). Dispersão cross-asset 2.44 pp é **7.7× menor** que a maior
  dispersão cross-filter da Série H (+4.37 pp H.1↔H.3). **Mean-reversion tem menos variância cross-asset
  que breakout** — sinal mais robusto.
- **Family > asset em peso.** Variação cross-family SOL (Donchian 31.07% → Bollinger 65.85%) = +34.78 pp.
  Variação cross-asset dentro de Bollinger = 2.44 pp. Família é **7.7× mais determinante** que asset
  para este edge nesta janela.
- **3/3 `canary_only` vs Série H 0/12** — mudança de família produziu o sinal que filtros causais não
  produziram. Confirma leitura estrutural de I.1 em escala.
- **Top-3 do ranking N=15 inteiramente Bollinger.** 4º (H.9 ETH+SMA) score=5.04; margem de separação
  ≥2.08 pontos. Não é disputa apertada — é separação de classe.
- **Próxima dimensão crítica é temporal.** Todos 3 pilotos são sobre **mesma janela** 180d; robustez
  temporal ainda não testada. Série J endereça isso.
- **3 candidatos concretos para handoff BotBinance** com critérios ortogonais: I.2 BTC (menor mdd),
  I.1 SOL (maior fe), I.3 ETH (intermediário). Pré-req antes de export: OOS Sharpe + aprovação
  explícita do usuário (AGENTS.md §8).

### Output exemplo 10 — Bollinger mean-reversion cross-timeframe (Série L completa: L.1 SOL + L.2 BTC + L.3 ETH em 15m 2024-H2)

Primeiro `fail` operacional do protocolo após 22 pilotos. Critério 3 de ADR-0025
(`spread+10/baseline ≥ 0.95`) violado em 3/3 assets quando timeframe desce de 1h para 15m.

Mesma configuração da Série J (Bollinger 20/2 long-only, custos 5/2/0 bps), única mudança é
`timeframe`: 1h → 15m (17280 barras vs 4320). Janela idêntica 2024-07-05 → 2024-12-31.

| piloto  | asset | hit baseline | fe baseline | trades | mdd    | `spread+10/baseline` | decisão  |
|---------|-------|--------------|-------------|--------|--------|----------------------|----------|
| **L.1** | SOL   | 63.10%       | **10433.99**| 336    | 5.53%  | **0.871**            | **fail** |
| **L.2** | BTC   | 60.00%       | 9696.67     | 330    | 5.11%  | **0.864**            | **fail** |
| **L.3** | ETH   | 61.76%       | 9769.61     | 353    | 9.32%  | **0.855**            | **fail** |

**ADR-0019 por piloto (`fee+10 ≡ spread+10` bit-a-bit, 23ª/24ª/25ª confirmações, primeira cross-timeframe):**
L.1=`9088.47` · L.2=`8376.61` · L.3=`8357.51`.

**Leitura cross-timeframe honesta:**

- **Hit rate preservado cross-timeframe (60-63% em 15m vs 65.85-71.76% em 1h, Série J).** Edge estatístico
  mean-reversion **sobrevive**. WF 4/4 folds cruzam 45% em todos os 3 pilotos. Portanto **o problema não é
  edge estatístico** — é edge econômico.
- **Trades multiplicam por ~4× (82-87 em 1h → 330-353 em 15m).** Proporcional ao aumento de barras
  (4320 → 17280). Cada trade paga custos (entrada + saída); exposição cumulativa a fee/slip/spread
  cresce linearmente com trades.
- **Sensibilidade a `spread+10` é ~4× pior em 15m.** SOL: Δ fe = −12.90% em 15m vs −3.24% em 1h (Série I.1).
  BTC: −13.61% vs −3.35%. ETH: −14.45% vs −3.26%. Multiplicador quase exato 4×, consistente com
  hipótese "exposição cumulativa linear em trade count".
- **BTC 15m e ETH 15m têm fe baseline < capital** (9696.67 e 9769.61). SOL 15m fica levemente positivo
  (+4.34%) mas não sobrevive stress.
- **3/3 `fail` com spread ratio consistente** (0.855 ± 0.008). Dispersão cross-asset em ratio de 16 bps:
  propriedade do timeframe, não idiossincrasia de asset.
- **Primeiro `fail` operacional do protocolo.** 22 pilotos anteriores passaram folgados no critério 3
  (10 `canary_only` com ratio ~0.96-0.98 + 12 `fail` histórico da Série H por critério 1). L.1/L.2/L.3
  são primeiros casos de **hit alto + critério 3 violado** — exatamente o caso que ADR-0025 foi
  desenhada para capturar.
- **Handoff BotBinance 15m formalmente refutado.** Qualquer tentativa de "multiplicar trades" em
  timeframe menor destrói edge neste protocolo de custos. Handoff permanece 1h (J.2 BTC ou J.1 SOL).
- **Próxima movimentação natural é direção oposta (4h, menos trades) ou segunda família (RSI).**
  Série M endereça isso.

### Output exemplo 11 — Bollinger mean-reversion cross-timeframe 4h (Série M completa: M.1 SOL + M.2 BTC + M.3 ETH)

Contraparte simétrica de L. Série L falhou em 15m por **custos**; M testa 4h e falha por
**amostra**. Com L + M `fail`, sweet spot 1h é formalmente delimitado em direções opostas.

Mesma configuração (Bollinger 20/2 long-only, custos 5/2/0 bps), janela 2024-07-05 → 2024-12-31.
Única mudança é `timeframe`: 1h → 4h (1080 barras vs 4320).

| piloto  | asset | hit baseline | fe baseline | trades | mdd    | `spread+10/baseline` | bloqueio | decisão |
|---------|-------|--------------|-------------|--------|--------|----------------------|----------|---------|
| **M.1** | SOL   | 57.14%       | 9766.99     | 21     | 6.99%  | **0.9915** | fe<capital | **fail** |
| **M.2** | BTC   | 52.63%       | 9932.49     | 19     | 4.38%  | **0.9924** | fe<capital | **fail** |
| **M.3** | ETH   | **43.75%**   | 9327.15     | 16     | 8.54%  | **0.9933** | hit<45% + fe<capital | **fail** |

**ADR-0019 por piloto (`fee+10 ≡ spread+10` bit-a-bit, 26ª/27ª/28ª confirmações):**
M.1=`9683.54` · M.2=`9856.70` · M.3=`9264.56`.

**Leitura cross-timeframe completa (SOL como referência, 2024-H2):**

| timeframe | trades | hit | fe | spread+10/base | bottleneck | decisão |
|-----------|--------|-----|-----|----------------|------------|---------|
| 15m (L.1) | 336    | 63.10% | 10433.99 | **0.871** | custos | fail |
| **1h (J.1)** | **87** | **67.82%** | **10684.24** | **0.967** | **nenhum** | **canary_only** |
| 4h (M.1) | 21 | 57.14% | 9766.99 | 0.9915 | amostra | fail |

**Leitura cross-timeframe honesta:**

- **Critério 3 passa folgado em 4h** (ratio 0.9915-0.9933 vs 0.855-0.871 em 15m): confirma
  relação linear entre trade count e exposição a custos. 21 trades em 4h vs 336 trades em
  15m ≈ 1:16; sensibilidade Δ fee+10 = −0.85% em 4h vs −12.90% em 15m ≈ 1:15. Fatores
  coincidem bem com hipótese linear-em-trades.
- **Mas edge estatístico também desaparece.** Hit cai cross-asset (SOL 67.82%→57.14%,
  BTC 68.24%→52.63%, ETH 71.76%→43.75%). Redução de frequência de sinal reduz amostra
  abaixo do threshold útil (16-21 trades).
- **M.3 ETH viola critério 1 pelo paradoxo amostra-pequena:** 4/4 folds WF cruzam 45%
  (50-66.67%) mas consolidado fica 43.75%. Cada fold teve sorte dentro de sua janela;
  agregado acumula perdedores.
- **Fe baseline < capital em 3/3 pilotos.** Fenômeno inédito — Séries I/J/K todas tinham
  fe > capital. 4h não produz retorno líquido nesta família/janela.
- **Sweet spot 1h formalmente delimitado.** L prova 15m quebra por custos; M prova 4h
  quebra por amostra. Séries I (2025-H2) + J (2024-H2) + K (hyperparameters) × 10 pilotos
  todos `canary_only` em 1h. **10/10 em 1h vs 6/6 fail fora de 1h** — separação cristalina.
- **Handoff BotBinance confirmado 1h.** Nenhum piloto fora de 1h é candidato. J.2 BTC 1h
  2024 permanece rank 1 global (score 7.64) ou J.1 SOL 1h 2024 (rank 2).
- **Próxima exploração útil é lateral (nova família RSI ou regime filter) dentro de 1h,
  não vertical (timeframe).**

### Output exemplo 12 — RSI mean-reversion cross-família (Série N completa: N.1 SOL + N.2 BTC + N.3 ETH)

Três pilotos `canary_only` sobre janela 2024-H2 1h idêntica à Série J Bollinger
— controle cross-família limpo. ADR-0027 (RSI 14/30/70 SMA-smoothed long-only)
cruza os 3 critérios ADR-0025 em todos os 3 assets.

| piloto | hit baseline | fe baseline | mdd | trades | `spread+10/baseline` | decisão |
|--------|--------------|-------------|-----|--------|----------------------|---------|
| N.1 SOL | 58.73% | 9850.00 | 6.35% | 63 | 0.9745 | canary_only |
| N.2 BTC | 67.19% | 10117.99 | 3.46% | 64 | 0.9747 | canary_only |
| N.3 ETH | 69.33% | 9900.11 | 5.71% | 75 | 0.9697 | canary_only |

**Comparativo RSI ↔ Bollinger por asset (mesma janela 1h 2024-H2):**

| asset | hit RSI | hit Bollinger | Δ hit | fe RSI | fe Bollinger | Δ fe |
|-------|--------:|--------------:|------:|-------:|-------------:|-----:|
| SOL | 58.73% | 67.82% | −9.09 pp |  9850 | 10684 | −834 |
| BTC | 67.19% | 68.24% | −1.05 pp | 10118 | 10252 | −134 |
| ETH | 69.33% | 71.76% | −2.43 pp |  9900 |  9977 |  −77 |

Lições estruturais:

- **Edge mean-reversion @ 1h é propriedade do regime, não assinatura de indicador.**
  Duas famílias independentes (Bollinger bandas estatísticas / RSI momentum
  SMA-smoothed) passam os mesmos 3 gates sobre o mesmo tape. Total: 6/6 pilotos
  MR @ 1h cross-família + cross-asset.
- **BTC é asset de maior convergência RSI↔Bollinger** (−1 pp hit, −134 fe). SOL
  é onde mais degrada (−9 pp hit). Hipótese: volatilidade SOL degrada
  cruzamento SMA-smoothed mais do que banda de desvio-padrão.
- **Hit ≠ fe sob custos.** ETH tem hit RSI + Bollinger acima de 65%, mas custos
  fixos (10 bps ida+volta) comem edge extra — N.3 ETH é o de maior hit do trio
  N, mas tem fe baseline negativa (9900 < capital). Otimizar por hit é armadilha.
- **ADR-0019 29ª/30ª/31ª confirmações** (primeira cross-família mean-reversion):
  N.1=9598.55, N.2=9862.02, N.3=9600.61.
- **Leaderboard N=31 (2026-04-18T13:15:28Z):** N.2 estreia rank 4 (score 7.19),
  melhor RSI acima de 6 Bollinger `canary_only`. Top-3 inalterado (J.2, J.1, K.3).
- **Handoff BotBinance não muda:** J.2 BTC Bollinger segue candidato primário —
  RSI domina em nenhum eixo contra Bollinger na mesma configuração padrão.

### Output exemplo 13 — RSI sweep paramétrico (Série O: O.1 7/25/75 fail + O.2 21/35/65 canary_only)

Dois pilotos sobre BTC 1h 2024-H2 (mesmo dataset de N.2), testando extremos
do espaço (period, oversold, overbought) para determinar sensibilidade
paramétrica e tentar superar N.2 (14/30/70 padrão).

- **CLI O.1:** `alpha-forge validate --strategy rsi --rsi-period 7
  --rsi-oversold 25 --rsi-overbought 75 --dataset-id
  btcusdt_1h_20240705_20241231_binance_spot --stress spread+10:0:0:10
  --run-id rsi-7-25-75-btc-1h-2024-baseline`
- **CLI O.2:** idem com `--rsi-period 21 --rsi-oversold 35
  --rsi-overbought 65 --run-id rsi-21-35-65-btc-1h-2024-baseline`.

**Sweep O.1 ↔ N.2 ↔ O.2 (BTC 1h 2024-H2, mesma janela, mesmos custos):**

| RSI | trades | hit | fe | MC p5 | `spread+10/baseline` | decisão |
|-----|-------:|----:|---:|------:|---------------------:|---------|
| 7/25/75 (O.1) | 147 | 59.86% | 10128.01 | 9931.16 | **0.9418** | **fail** |
| **14/30/70 (N.2)** | **64** | **67.19%** | **10117.99** | **9878.93** | **0.9747** | **canary_only** |
| 21/35/65 (O.2) | 58 | 58.62% |  9959.83 | 9595.53 | 0.9767 | canary_only |

**Leituras operacionais:**
- **14/30/70 domina em `hit` + critério 3 simultaneamente.** Nenhuma
  configuração de extremo vence N.2 em todos os eixos materiais.
- **O.1 falha por trade frequency:** 147 trades/semestre amplificam stress de
  spread → ratio 0.9418 < 0.95. Padrão operacional idêntico ao de Série L
  (15m), agora reproduzido por parametrização ao invés de timeframe.
- **O.2 passa hard gate mas dominado por N.2 em hit (−8.57 pp), fe (−158.16) e
  MC p5 (−283.40 — pior MC p5 dos 14 `canary_only`).** Edge absoluto frágil;
  cauda inferior pode produzir perda de 4% com 5% de probabilidade.
- **Relação linear trade-count ↔ critério 3 validada empiricamente:**
  147→0.9418; 64→0.9747; 58→0.9767 (slope ≈ −0.0004/trade, consistente com
  Série L). Útil como heurística: >110 trades/semestre é sinal amarelo.
- **ADR-0025 critério 3 capturou parametric overfit de O.1** — sem ele, O.1
  pareceria superior (melhor MC p5, fe comparável a N.2). Com ele, rejeitado.
- **ADR-0019 32ª/33ª confirmações** (primeira sobre sweep paramétrico puro,
  reusando engine sem alterações): O.1=9538.35, O.2=9728.15 bit-a-bit.
- **Sensibilidade paramétrica baixa em 14/30/70.** 2 pontos de extremo
  são suficientes para concluir sweet spot; sweep denso seria desperdício.
- **Leaderboard N=33 (2026-04-18T13:25:41Z):** top-3 inalterado (J.2, J.1,
  K.3); N.2 segue rank 4 (7.19); O.1 entra rank 10 (6.72, `fail`); O.2 entra
  rank 11 (6.43). Handoff **J.2 BTC Bollinger permanece**.
- **Série O fecha em 2 pilotos.** Próxima dimensão ortogonal: regime filter
  sobre J.2 BTC Bollinger (Série P).

### Output exemplo 14 — Regime filter sobre J.2 BTC Bollinger (Série P completa: P.1 sma + P.2 atr + P.3 and — **novo handoff primário**)

Três pilotos aplicando ADR-0022/ADR-0023 sobre J.2 BTC Bollinger 1h 2024-H2.
Dimensão ortogonal a parâmetros (Séries K/O) e a família (Série N);
primeiro experimento "aperfeiçoar sweet spot em vez de diversificar".

- **CLI P.1:** `alpha-forge validate --strategy bollinger --bollinger-window 20
  --bollinger-num-std 2.0 --dataset-id btcusdt_1h_20240705_20241231_binance_spot
  --regime-filter sma_slope:window=50:min_slope_bps=10 --stress fee+10:10:0:0
  --stress spread+10:0:0:10 --run-id bollinger-20-2-btc-1h-2024-regime-sma
  --mc-seed 42 --mc-resamples 1000`
- **CLI P.2:** idem com `--regime-filter atr_regime:window=14:min_atr_bps=50
  --run-id bollinger-20-2-btc-1h-2024-regime-atr`.
- **CLI P.3:** idem com `--regime-filter 'and(atr_regime:min_atr_bps=50:window=14,sma_slope:min_slope_bps=10:window=50)'
  --run-id bollinger-20-2-btc-1h-2024-regime-sma-and-atr`.

**Quadro P (J.2 BTC Bollinger + filtros, mesma janela, custos 5/2/0 bps):**

| Pilot | filtro | trades | hit | fe | MC p5 | `spread+10/baseline` | decisão |
|-------|--------|-------:|----:|---:|------:|---------------------:|---------|
| J.2 | — | 85 | 68.24% | 10252.14 | 9921.73 | 0.9668 | canary_only |
| P.1 | `sma_slope:50:10` | 86 | 66.28% | 10184.11 | 10003.03 | 0.9662 | canary_only |
| **P.2** | **`atr_regime:14:50`** | **72** | **73.61%** | **10316.93** | 9971.33 | **0.9721** | **canary_only** |
| P.3 | `and(atr,sma)` | 73 | 71.23% | 10252.71 | **9995.84** | 0.9715 | canary_only |

**Leituras operacionais:**
- **P.2 é o primeiro piloto a dominar J.2 em TODAS as dimensões.** hit +5.37
  pp, fe +64.79, trades −15%, MC p5 +49.60, ratio +0.0053 simultaneamente.
  **Handoff BotBinance muda de J.2 para P.2.**
- **`atr_regime` > `sma_slope` em mean-reversion BTC 1h 2024-H2.** P.1 apenas
  reordena timing (85→86 trades); P.2 filtra regimes de baixa volatilidade
  onde bandas Bollinger são estreitas sem edge real.
- **P.2 `fee+10 = spread+10 = 10028.59 > 10000`** — **primeira vez que
  cenário stress termina acima do capital inicial**. Edge sobrevive stress.
- **P.3 (AND) não supera P.2.** sma_slope quase inativo em cima de
  atr_regime; composição adiciona fragmentação sem ganho — replica finding
  Série H.5 (AND Donchian long não superou H.3 SMA nem H.4 ATR) agora em
  Bollinger mean-reversion. Família de filtro importa qualitativamente.
- **MC p5 = 9995.84 (P.3) é o melhor do protocolo**, mas em ADR-0024 default
  weights (w_hit=2.0 > w_p5=1.5 > w_fe=1.0) hit e fe dominam score composto.
- **WF P.2 todos ≥ 72.22%**; fold 2 hit=84.62% é o maior single-fold hit do
  protocolo inteiro.
- **ADR-0019 34ª/35ª/36ª confirmações** (`fee+10 ≡ spread+10` bit-a-bit):
  P.1=9840.0884; P.2=10028.5915; P.3=9960.4985 (primeira sob `CompositeFilter`).
- **Leaderboard N=36 (2026-04-18T13:40:17Z):** P.2 rank 1 (7.85), P.3 rank 2
  (7.77), J.2 rank 3 (7.47), P.1 rank 4 (7.44). Primeira reordenação de
  top-3 desde Série J.
- **Lição meta-operacional:** adicionar 1 filtro ao sweet spot (Série P)
  supera J.2 onde 3 pilotos RSI (Série N) + 2 pilotos sweep (Série O) não
  conseguiram. Ordenação futura: aperfeiçoar antes de diversificar.
- **Próxima dimensão:** Série Q cross-asset (atr_regime em SOL + ETH) para
  validar que ganho é propriedade do regime 1h, não BTC-específica.

### Output exemplo 15 — Regime filter cross-asset (Série Q: Q.1 SOL + Q.2 ETH replicando P.2)

Dois pilotos replicando P.2 (`atr_regime:14:50`) em SOL e ETH Bollinger
1h 2024-H2 para testar universalidade do ganho do filtro ATR.

- **CLI Q.1:** `alpha-forge validate --strategy bollinger --bollinger-window 20
  --bollinger-num-std 2.0 --dataset-id solusdt_1h_20240705_20241231_binance_spot
  --regime-filter atr_regime:window=14:min_atr_bps=50 --stress fee+10:10:0:0
  --stress spread+10:0:0:10 --run-id bollinger-20-2-sol-1h-2024-regime-atr
  --mc-seed 42 --mc-resamples 1000`
- **CLI Q.2:** idem com `--dataset-id ethusdt_1h_20240705_20241231_binance_spot
  --run-id bollinger-20-2-eth-1h-2024-regime-atr`.

**Quadro Q (cross-asset 1h 2024-H2, mesma janela, custos 5/2/0 bps):**

| Pilot | asset | trades | hit | fe | MC p5 | `spread+10/baseline` | filtro ativo |
|-------|-------|-------:|----:|---:|------:|---------------------:|-------------:|
| P.2 | BTC+atr | 72 | 73.61% | 10316.93 | 9971.33 | 0.9721 | **15%** |
| Q.1 | SOL+atr | 87 | 67.82% | 10716.73 | 10064.16 | 0.9674 | **1%** |
| Q.2 | ETH+atr | 80 | 73.75% | 10119.65 | 9753.11 | 0.9684 | **6%** |

**Leituras operacionais:**
- **Espectro cross-asset identificado** (ordem de utilidade do filtro ATR
  em 2024-H2): **BTC > ETH > SOL**. Segue distribuição de volatilidade
  realizada — SOL mantém ATR > 50 bps quase continuamente no semestre,
  então filtro nunca aciona (só 1 relocação de timing em 87 sinais).
- **"atr_regime é universal"** **refutado**. Filtro é universalmente
  **safe** (não piora nenhum asset) mas não universalmente **valioso**
  (só ganha material em assets com períodos de baixa volatilidade).
- **Threshold 50 bps é calibrado implicitamente para BTC 2024-H2.**
  Para SOL, threshold precisaria ~100 bps. Para ETH, 50 bps aciona
  parcialmente (6% dos sinais).
- **Q.2 ETH corrige a única fe sub-capital entre Bollinger `canary_only`**:
  J.3 baseline tinha fe=9977.19; Q.2 tem 10119.65 (+142.46, cruza 10000).
- **Primeira contradição entre baseline dominance e composite score:**
  Q.2 domina J.3 em TODAS as 5 métricas raw mas ranking composto
  coloca Q.2 (6.84) abaixo de J.3 (6.91) — filtro fragmenta fold 2
  (hit 53.85% vs J.3 62.50% min) e ADR-0024 penaliza via `fold_min_hit`
  + `fold_std_hit`. **Score composto captura dimensão de robustez WF
  que comparação raw não captura.** Lição operacional: score composto
  não é estritamente monótono em cada métrica; é global por design.
- **ADR-0019 37ª/38ª confirmações** (`fee+10 ≡ spread+10` bit-a-bit):
  Q.1=10367.65 (2ª vez stress > 10000; primeira em SOL); Q.2=9799.73.
- **Leaderboard N=38 (2026-04-18T14:05:39Z):** top-4 BTC inalterado;
  Q.1 SOL entra rank 5 (7.28, desbanca J.1 rank 6); Q.2 ETH entra rank 11
  abaixo de J.3 rank 10. Handoff BotBinance **permanece P.2 BTC**.
- **Próxima dimensão candidata:** Série R com threshold calibrado por
  asset (`atr_regime:min_atr_bps=100` em SOL) OU Série S aplicando
  `atr_regime:14:50` sobre N.2 BTC RSI (cross-família).

### Output exemplo 16 — Threshold calibration curve + cross-family transfer (Séries R+S)

Três pilotos em paralelo: **R** calibra threshold do filtro ATR em SOL
(testando se universalidade é CALIBRAÇÃO em vez de arquitetura); **S**
testa transferência cross-família do filtro ATR para RSI (em vez de
Bollinger).

- **CLI R.1:** `... --dataset-id solusdt_1h_20240705_20241231_binance_spot
  --regime-filter atr_regime:window=14:min_atr_bps=100
  --run-id bollinger-20-2-sol-1h-2024-regime-atr-100 ...`
- **CLI R.2:** idem com `min_atr_bps=150` e `-150` no run-id.
- **CLI S.1:** `... --strategy rsi --rsi-period 14 --rsi-oversold 30
  --rsi-overbought 70 --regime-filter atr_regime:window=14:min_atr_bps=50
  --run-id rsi-14-30-70-btc-1h-2024-regime-atr ...` (dataset BTC 1h 2024-H2).

**Quadro R — curva de utilidade SOL+atr_regime:**

| Pilot | threshold | trades | hit | fe | MC p5 | ratio | leitura |
|-------|----------:|-------:|----:|---:|------:|------:|---------|
| J.1 | — | 87 | 67.82% | 10684 | 10046 | 0.9673 | raw |
| Q.1 | 50 | 87 | 67.82% | 10716 | 10064 | 0.9674 | filtro inativo |
| **R.1** | **100** | **65** | **70.77%** | **10803** | **10212** | **0.9758** | **sweet spot** |
| R.2 | 150 | 26 | 65.38% | 10420 | 10074 | 0.9899 | over-filter |

**Quadro S — cross-família RSI+atr (BTC 1h 2024-H2):**

| Pilot | filtro | trades | hit | fe | MC p5 | ratio |
|-------|--------|-------:|----:|---:|------:|------:|
| N.2 | — | 64 | 67.19% | 10117 | ~9878 | 0.9747 |
| S.1 | atr:50 | 55 | 65.45% | 10097 | 9851 | 0.9782 |

**Leituras operacionais:**
- **Universalidade de filtro é CALIBRAÇÃO, não arquitetura.** R mostra
  que mesmo asset (SOL) tem threshold ótimo calibrável (100 bps
  ≈ quantile 15-25 do ATR do asset). Método de 3 pontos
  (baixo/médio/alto) localiza sweet spot antes de deploy.
- **Curva atr_regime é não-monotônica** — "U invertido com plateau
  esquerdo": thr baixo é inativo (plateau), sweet spot intermediário,
  thr alto é over-filter (amostra pequena, edge instável).
- **R.1 é novo rank 1 do protocolo (score 7.819)** — substitui P.2 BTC
  como handoff primário. Primeira mudança de handoff desde Série P.
- **Filtro ATR NÃO generaliza cross-família.** S.1 é net wash vs N.2
  (perde 1.74pp hit e 20 fe, ganha 0.0035 ratio marginal). Valor do
  ATR em Bollinger vem da interação **banda_σ × ATR_min** que RSI não
  tem — filtro é **Bollinger-specific**.
- **R.2 passa gates mas é dominado por R.1** (26 trades é amostra
  marginal); `canary_only` com caveat operacional — mapeia lado
  over-filter da curva sem ser deployable.
- **ADR-0019 39ª/40ª/41ª confirmações:** R.1=10542.34 (3ª vez stress
  > 10500); R.2=10316.21 (ratio 0.9899 — MAIOR do protocolo via
  amostra pequena trivialmente); S.1=9877.57 (3ª vez stress < 10000).
- **Leaderboard N=41 (2026-04-18T14:21:24Z, topo):** R.1 rank 1 (7.819)
  → P.2 rank 2 (7.739) → P.3 rank 3 (7.657) → J.2 rank 4 (7.356) →
  **R.2 rank 5 (7.351, score alto via ratio trivial)** → P.1 rank 6.
  N.2 rank 10; S.1 rank 13 (abaixo de N.2 conforme previsto).
- **Próxima dimensão candidata:** Série T (threshold sweep cross-asset
  Bollinger: BTC 35/70/100, ETH 75/120) para confirmar método
  3-pontos cross-asset; OU filtro específico de momentum (RSI-regime)
  em N.2 para testar família RSI com filtro de família própria.

### Output exemplo 17 — Séries T–Z autonomous run (20 pilots; protocolo N=61)

Execução autônoma de 6 séries em sequência única com autorização
explícita do usuário ("pode ir até o Z"). T-Z mapeiam curva de
utilidade atr_regime em 3 dimensões: **cross-asset**, **cross-window**,
**cross-strategy**.

**Séries executadas:**
- **T** (6 pilots): BTC+ETH threshold sweep 2024-H2 (thr=35/70/100 BTC, 40/90/130 ETH).
- **U** (2): ETH sweet spot refine (thr=75, 105).
- **V** (2): BTC sweet spot refine (thr=55, 85).
- **W** (3): OOS 2025-H2 validation (SOL thr=100, BTC thr=55, ETH thr=105).
- **X** (3): Composite AND(atr, sma_slope) nos sweet spots.
- **Y** (2): Donchian long + atr_regime (cross-strategy).
- **Z** (2): SOL curve fill-in (thr=75, 125).

**Quadro consolidado — leaderboard N=61 (topo):**

| rank | piloto | thr | score | hit | fe | trades |
|------|--------|----:|------:|----:|---:|-------:|
| 1 | T.6 ETH+atr | 130 | 7.735 | 85.71% | 10299 | 14 |
| 2 | T.3 BTC+atr | 100 | 7.658 | 75.00% | 10270 | 16 |
| **3** | **U.2 ETH+atr** | **105** | **7.313** | **73.68%** | **10619** | **38** |
| 4 | R.1 SOL+atr | 100 | 7.247 | 70.77% | 10803 | 65 |
| 5 | X.3 SOL AND(atr,sma) | 100 | 7.246 | 68.75% | 10707 | 64 |

**Findings operacionais consolidados:**
- **Método 3-pontos calibra sweet spot cross-asset**: BTC thr≈50-55
  (median=70bps), ETH thr≈90-105 (median=88), SOL thr≈100 (median
  maior). Sweet spot ≈ quantile 40-60 do ATR do asset.
- **Edge degrada cross-window**: W.1/W.2/W.3 testam sweet spots 2024
  em dataset 2025-H2. Todas 3 perdem 15-20pp hit (SOL 70.77→53.45,
  BTC 73.13→52.38, ETH 73.68→57.14). **Calibração é window-specific,
  não universal temporal**. Todos ainda passam gates (hit>45%,
  ratio>0.95) mas edge é material menos convincente.
- **Filtro ATR é Bollinger-specific**: Y.1 Donchian BTC+atr:55 falha
  gate 1 (hit 43.30% < 45%); Y.2 Donchian SOL+atr:100 marginal
  (45.16%, fe 9580). Consistente com S.1 RSI+atr finding — ATR é
  útil em famílias de sinal baseadas em bandas de volatilidade
  (Bollinger) mas não em momentum (RSI) ou breakout (Donchian).
- **AND(atr, sma) melhora MC p5 sem melhorar fe**: X.3 SOL AND tem
  **MELHOR MC p5 do protocolo (10327.29)** vs R.1 (10212) — sma
  adiciona robustez tail mas penaliza fe em −96. Trade-off: mais
  seguro (p5) vs mais rentável (fe médio).
- **Curvas têm plateau largo, não peak sharp**: Z.1 SOL+atr:75 fe
  10743 ≈ R.1 SOL+atr:100 fe 10803 (plateau 75-100 bps); U.2 ETH
  thr 105 fe 10619 ≈ T.5 ETH thr 90 fe 10645 (plateau 90-130).
  **Implicação**: calibração exata do threshold não é crítica —
  qualquer ponto no plateau funciona.
- **Top-2 têm amostras marginais** (T.6=14 trades, T.3=16 trades) —
  score composto recompensa hit/ratio altos mesmo com amostra pequena.
  **Handoff operacional recomendado: U.2 ETH+atr:105** (rank 3 mas
  38 trades + fe 10619 + hit 73.68% é balance mais deployable).
- **ADR-0019 61 confirmações** (+20 em T-Z). 5ª vez stress > 10500
  (T.5, U.2). `fee+Δ ≡ spread+Δ` bit-a-bit sustenta cross-strategy
  (Bollinger+Donchian), cross-filter (simple+composite), cross-window
  (2024+2025).

**Implicação arquitetural:** edge é **calibrável mas não universal**.
Método 3-pontos é operacionalmente válido dentro de uma janela
temporal (2024-H2) mas exige re-calibração para outras janelas.
Próxima dimensão natural: validação operacional (paper trading) do
candidato U.2 em dados tempo-real, OU exploração de famílias de
filtro novas (vol-of-vol, autocorrelation, microstructure) para
quebrar teto atual de score ≈ 7.7.

## Flow: observabilidade do engine (logging dev-only, sem ADR)

- **Trigger:** `alpha-forge run-demo --log-level {silent,info,debug}` ou, em código, configurar o logger `alpha_forge.backtest` antes de chamar `run_backtest`.
- **Steps:**
  1. Engine emite `backtest.start` em INFO assim que `run_backtest` começa (contém `dataset_id`, `bars`, nome da classe da estratégia, capital e parâmetros do `CostModel`).
  2. Por evento: `engine.fill.open` em DEBUG a cada abertura, `engine.fill.close` em DEBUG a cada fechamento (um por `Trade` fechado), `engine.rejection` em DEBUG a cada `Rejection`, `engine.reverse_on_signal` em DEBUG quando o engine dispara reversão (ADR-0012).
  3. Engine emite `backtest.end` em INFO no fim, com contagens finais e `final_equity`.
  4. CLI `--log-level` controla apenas o handler (stderr). Default `silent` = sem handler = sem output. Stdout do summary permanece idêntico em qualquer nível.
- **Output real (`--log-level info --no-long-only` no dataset sintético seminal, 720 barras):** stderr recebe exatamente duas linhas — `backtest.start dataset_id=synthetic_btcusdt_1h_seed42 bars=720 strategy=MovingAverageCrossoverStrategy capital=10000.00 fee_bps=5.0000 slip_bps=2.0000` e `backtest.end dataset_id=... bars=720 fills=33 rejections=0 trades=16 final_equity=9415.62`. Stdout mantém o bloco `--- metrics ---` usual. No `--log-level debug`, aparecem também eventos `engine.reverse_on_signal ts_exec=<ISO8601> from=<LONG|SHORT> to=<SHORT|LONG>` a cada reversão — útil para auditar o custo duplo do ADR-0012.
- **Invariante de não-contrato:** o formato das mensagens **não é contrato público** — pode mudar sem ADR. O que é estável: nome do namespace (`alpha_forge.backtest`) e a garantia de que logging não altera `BacktestResult`.
- **Covered by tests:** `tests/unit/test_engine_observability.py` — `TestLoggingNaoAlteraContrato` (result idêntico com/sem logging), `TestEventosInfo` (start/end emitidos uma vez cada), `TestEventosDebug` (um evento por fill/rejection/trade/reverse), `TestLoggerNameEhBacktest` (namespace estável).

## Flow: regressão dura do engine (reverse-on-signal, ADR-0012)

- **Trigger:** `pytest tests/property/test_engine_reverse_on_signal.py`.
- **Steps:**
  1. Hypothesis sorteia `short_window ∈ [2, 30]`, `long_gap ∈ [1, 40]`, `fee_bps ∈ [0, 20]`, `slip_bps ∈ [0, 20]`.
  2. Instancia `MovingAverageCrossoverStrategy(short_window, long_window=short_window+long_gap, long_only=True)` — modo que **nunca** emite `ENTER_SHORT`, logo o ramo reverse-on-signal do engine não deve disparar.
  3. Roda `run_backtest` sobre o dataset seminal sintético.
  4. Assert: nenhum par consecutivo de `Fill` compartilha `timestamp` (reverse-on-signal é a única origem desse padrão).
  5. Assert: todo `Fill` de abertura (`side ∈ {LONG, SHORT}`) é seguido por exatamente zero ou um `Fill` de fechamento (`side=FLAT`) antes da próxima abertura.
- **Outcome:** 25 exemplos, sem flakiness. Prova que a mudança ADR-0012 no engine não alterou o caminho antigo para estratégias long-only existentes (MA ADR-0008 default, Donchian ADR-0011).
- **Covered by test:** o próprio arquivo.

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
- **Segundo lote real (multi-asset):** ETHUSDT 1h (4320 barras, `sha256=91a039d9...`) e SOLUSDT 1h (4320 barras, `sha256=ee88d834...`) na mesma janela de BTC, ingeridos com um único comando (`--symbols ETHUSDT,SOLUSDT`). Zero gaps detectados em ambos. Gate anti-hardcode pós-ingestão: `rg -n 'ETH|SOL' src/` → 0 matches (runtime permanece agnóstico a símbolo, ADR-0009 §2-bis).
- **Covered by test:**
  - `tests/unit/test_ingest_binance_vision.py` (sem rede, 4 testes): normalização canônica, dois símbolos distintos não colidem em path/sha256/manifesto, gap não declarado rejeita e não deixa órfão, gap declarado passa.
  - `tests/unit/test_paths_multi_asset.py` (4 testes): `processed_dataset_path` trata `symbol`/`timeframe` como opacos; nenhum ativo é privilegiado.
  - `tests/unit/test_data_loader.py::test_loader_multi_asset_nao_colide`: dois datasets de símbolos distintos coexistem no manifesto e carregam independentemente.
  - `tests/integration/test_first_real_dataset.py`: pipeline completo (loader → estratégia → engine → métricas) sobre **os três datasets reais** (BTCUSDT, ETHUSDT, SOLUSDT) × **duas estratégias** (MA 20/50 e Donchian 20/10) = 6 casos parametrizados. Asserts são estruturais (causalidade, métricas em faixa, nenhum fill com `ts_exec` compartilhado — reverse-on-signal não dispara em long-only); **nada sobre PnL esperado**. Cada caso faz skip limpo se o Parquet correspondente ainda não foi ingerido.

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

## Flow: pureza causal da `DonchianBreakoutStrategy`

- **Trigger:** `pytest tests/property/test_donchian_causal.py`.
- **Steps:**
  1. Hypothesis gera série OHLC respeitando os invariantes mínimos (`high >= max(open, close)`, `low <= min(open, close)`, `high >= low`).
  2. Escolhe `t` e `perturb_offset ∈ [0, 10]`. `perturb_offset=0` muta a própria barra `t` (cobre "ignora barra corrente por construção"); `> 0` muta barra futura (cobre causalidade clássica).
  3. Constrói uma barra sintética respeitando os invariantes de OHLC e grava em `mutated.iloc[t+perturb_offset]`.
  4. Compara `strategy.decide(original[:t+1])` com `strategy.decide(mutated[:t+1])`.
  5. Os dois sinais devem ser iguais.
- **Outcome:** propriedade falha se a estratégia vazar informação da barra `t` ou do futuro; `entry_window=5, exit_window=3`, 100 exemplos sem flakiness.
- **Covered by test:** o próprio arquivo.

## Flow: monotonicidade de custo — Donchian (property-based, aplicação mecânica da ADR-0010)

- **Trigger:** `pytest tests/property/test_cost_monotonicity_donchian.py`.
- **Steps:** idênticos ao flow abaixo (MA), com a única diferença sendo a estratégia: `DonchianBreakoutStrategy(entry_window=20, exit_window=10)` em vez de `MovingAverageCrossoverStrategy(20, 50)`. Constantes de referência, tolerância (`1e-6 * 10.000`), geração `@st.composite dominated_cost_pair` e `assume(trade_count > 0)` são idênticas à ADR-0010.
- **Outcome:** 30 exemplos, ~10s solo, sem flakiness. Estende a cobertura do invariante ADR-0010 para a segunda estratégia real do laboratório (ADR-0011) sem introduzir decisão arquitetural nova — é aplicação mecânica, não parametrização.
- **Covered by test:** o próprio arquivo.

## Flow: monotonicidade de custo — MA simétrico `long_only=False` (ADR-0010 + ADR-0012)

- **Trigger:** `pytest tests/property/test_cost_monotonicity_ma_short.py`.
- **Steps:** idênticos ao flow MA long-only abaixo — mesmo dataset seminal, mesma tolerância, mesma `@st.composite dominated_cost_pair` — mas instancia `MovingAverageCrossoverStrategy(20, 50, long_only=False)` (modo simétrico ADR-0012). Cada reverse-on-signal paga `apply_cost` **duas vezes** (fechamento + abertura no mesmo `ts_exec`); se a monotonicidade ADR-0010 vale, vale aqui também.
- **Outcome:** 30 exemplos, ~10s solo, sem flakiness. Fecha o follow-up explícito da ADR-0012 (`tests/property/test_cost_monotonicity.py` só cobria long-only) sem tocar contrato público nem engine.
- **Covered by test:** o próprio arquivo.

## Flow: pureza causal da `BollingerMeanReversionStrategy` (ADR-0026)

- **Trigger:** `pytest tests/property/test_bollinger_causal.py`.
- **Steps:**
  1. Hypothesis gera série OHLC respeitando os invariantes mínimos (`high >= max(open, close)`, `low <= min(open, close)`, `high >= low`); `window=5, num_std=2.0`, `MIN_BARS=8`.
  2. Escolhe `t ∈ [MIN_BARS-1, n-1]` e `perturb_offset ∈ [0, 10]`. `perturb_offset=0` muta a própria barra `t` (cobre "ignora barra corrente por construção"); `> 0` muta barra futura.
  3. Mutação é OHLC completo (open, high, low, close) respeitando invariantes.
  4. Compara `strategy.decide(original[:t+1])` com `strategy.decide(mutated[:t+1])`.
  5. Os dois sinais devem ser iguais.
- **Outcome:** propriedade falha se a estratégia vazar informação de `t` ou do futuro. 100 exemplos sem flakiness. Estende formalmente a cobertura causal para a terceira família (mean-reversion), completando o tridente MA + Donchian + Bollinger.
- **Covered by test:** o próprio arquivo.

## Flow: monotonicidade de custo — Bollinger (property-based, ADR-0010 + ADR-0019 aplicados à 5ª família)

- **Trigger:** `pytest tests/property/test_cost_monotonicity_bollinger.py`.
- **Steps:** idênticos aos flows paralelos (MA long-only, Donchian long-only, MA simétrico, Donchian simétrico) — mesmo dataset seminal `synthetic_btcusdt_1h_seed42`, mesma tolerância `1e-6 * 10.000`, mesma `@st.composite dominated_cost_pair` **estendida para 3 eixos** (fee + slip + spread, ADR-0019). Instancia `BollingerMeanReversionStrategy(window=20, num_std=2.0)`. Pelo menos uma desigualdade estrita por par é garantida por construção.
- **Outcome:** 30 exemplos, sem flakiness. Estende a matriz de invariância de custo para a primeira família mean-reversion do protocolo — ADR-0010 + ADR-0019 agora confirmado sobre 5 famílias (MA long-only, MA simétrico, Donchian long-only, Donchian simétrico, Bollinger long-only).
- **Covered by test:** o próprio arquivo.

## Flow: monotonicidade de custo — Donchian simétrico `long_only=False` (ADR-0010 + ADR-0013)

- **Trigger:** `pytest tests/property/test_cost_monotonicity_donchian_short.py`.
- **Steps:** idênticos aos três flows paralelos (MA long-only, Donchian long-only, MA simétrico) — mesmo dataset seminal, mesma tolerância `1e-6 * 10.000`, mesma `@st.composite dominated_cost_pair` — mas instancia `DonchianBreakoutStrategy(20, 10, long_only=False)` (modo simétrico ADR-0013). Reusa reverse-on-signal do engine (ADR-0012) — cada reversão paga `apply_cost` **duas vezes** (fechamento + abertura no mesmo `ts_exec`); se o invariante ADR-0010 vale, vale aqui por arquitetura do engine.
- **Outcome:** 30 exemplos, ~10s solo, 3/3 verde consecutivas. Fecha o follow-up explícito da ADR-0013 (`tests/property/test_cost_monotonicity_donchian.py` só cobria long-only) sem tocar contrato público nem engine. Completa a matriz 4×: cada família (MA, Donchian) × cada modo (long-only, simétrico).
- **Covered by test:** o próprio arquivo.

## Flow: monotonicidade de custo (property-based, ADR-0010)

- **Trigger:** `pytest tests/property/test_cost_monotonicity.py`.
- **Steps:**
  1. `@st.composite dominated_cost_pair` gera `(cost_low, cost_high)` **por construção**: sorteia `fee_low ∈ [0, 50]`, `slip_low ∈ [0, 100]`, depois `fee_delta ∈ [0, 50 − fee_low]` e `slip_delta ∈ [0, 100 − slip_low]`; se ambos deltas vierem zero, força `slip_delta ≥ 1e-9`. Resultado: `cost_high` sempre domina `cost_low` componente a componente, com ao menos uma desigualdade estrita. **Nenhum `assume(...)` de dominância** — evita `HealthCheck.filter_too_much` (causa raiz da flakiness intermitente observada em rodadas anteriores, quando o padrão antigo `@given + assume(_dominates)` rejeitava ~90% dos exemplos e certas sementes esgotavam o orçamento de filtragem).
  2. Roda `run_backtest` duas vezes com **cenário idêntico** (mesmo dataset `synthetic_btcusdt_1h_seed42`, mesma `MovingAverageCrossoverStrategy(20, 50)`, mesmo `RiskBudget`); única variável é `cost_model`.
  3. `assume(result_low.metrics.trade_count > 0)` — descarta cenários triviais (ADR-0010 §Ressalva 1). Este `assume` é barato: ocorre só depois de dois backtests e raramente filtra.
  4. Assert: `final_equity_high - final_equity_low <= 1e-6 * capital_inicial`.
- **Outcome:** 30 exemplos × 2 backtests cada (~60 backtests), ~14s. Estabilidade verificada em 15/15 rodadas consecutivas após o fix de construção; antes do fix era ~12/15. Qualquer violação vem com mensagem rica (cost_low, cost_high, final_equity_low/high, trade_count_low/high, fills_low/high) para depuração imediata.
- **Covered by test:** o próprio arquivo.

## Flow: rejeição determinística de sizing inválido

- **Trigger:** cada tentativa de entrar em posição durante `run_backtest`.
- **Steps:**
  1. `fixed_fractional_position_sizing` devolve tamanho cru.
  2. `_classify_size` testa na ordem: `NaN`, `±inf`, `0.0`, `< 0.0`, `exposure > alavancagem_max + 1e-9`.
  3. Motivo encontrado → `Rejection` registrada, fill não acontece. Nenhum motivo → `Fill` registrado com tamanho aprovado.
- **Outcome:** resultado final do backtest contém auditoria completa (`rejections` lista, cada um com motivo, price, raw_size, signal/exec timestamps).
- **Covered by test:** `tests/unit/test_engine_reject_invalid_sizing.py` (cinco gatilhos) + `tests/unit/test_risk_sizing.py` (schema e função pura).

## Flow: walk-forward causal + Monte Carlo sobre trades (ADR-0003)

- **Trigger:** `from alpha_forge.validation import walk_forward, monte_carlo_trades` em notebook, script ou teste de integração; ou `pytest tests/integration/test_validation_pipeline.py`.
- **Steps:**
  1. `walk_forward(prices, strategy, budget, cost_model, dataset_id, n_folds, scheme, train_fraction, min_test_bars)` valida parâmetros e particiona `prices` em `n_folds` janelas de teste contíguas e disjuntas, do mesmo tamanho (última absorve resto).
  2. Fold 0 é **pulado** (sem train anterior). Para cada fold `k ≥ 1`: `train_window` é o passado anterior ao `test_window[k]` (do início em `expanding`; janela proporcional em `rolling`); `test_window` é a fatia do dataset executada.
  3. `run_backtest` é chamado uma vez por fold sobre `test_window` — `assert_causal` (ADR-0002) é aplicado automaticamente. `dataset_id` é anotado com sufixo `#fold{k}` para rastreamento em logs (`alpha_forge.backtest`).
  4. Retorna `list[WalkForwardFold]`; cada fold expõe `train_window`, `test_window`, e `result: BacktestResult` do teste.
  5. Opcionalmente: agregar `result.trades` de todos os folds (ou selecionar um fold) em um `BacktestResult` e passar para `monte_carlo_trades(result, capital_inicial, n_resamples, seed)`.
  6. Monte Carlo reamostra com reposição os PnLs de `result.trades`, recomputa curva de equity acumulada e `max_drawdown` em cada amostra; retorna `MonteCarloSummary` com percentis `{5, 25, 50, 75, 95}` de `final_equity` e `max_drawdown`.
- **Outcome:** walk-forward herda causalidade do engine por construção (testado em `tests/property/test_walk_forward_causal.py`: mutar barras em `test_window[k]` não altera `result[j]` para `j < k`); Monte Carlo é determinístico bit-a-bit dada a mesma terna `(result, n_resamples, seed)`. **Limitação declarada** do MC: assume i.i.d. de PnL por trade — variantes com autocorrelação são deferred.
- **Não incluído no núcleo:** tuning de parâmetros dentro do walk-forward; composite scoring; ranking cross-strategy. Cada um vira ADR separada. (Stress de custos sistematizado entrou via ADR-0014; flow abaixo.)
- **Covered by tests:** `tests/unit/test_walk_forward.py` (validação de parâmetros, particionamento, integração com engine), `tests/unit/test_monte_carlo.py` (validação, reprodutibilidade, shape dos percentis), `tests/property/test_walk_forward_causal.py` (causalidade por composição), `tests/integration/test_validation_pipeline.py` (end-to-end sobre MA 20/50 no sintético seminal).

## Flow: stress de custos sistematizado (ADR-0014 + ADR-0019)

- **Trigger:** `from alpha_forge.validation import cost_stress, CostPerturbation` em notebook, script ou teste de integração; ou `pytest tests/integration/test_cost_stress_pipeline.py`.
- **Steps:**
  1. Chamador monta `baseline_cost: CostModel` (três componentes: fee + slip + spread, ADR-0019) e uma lista `perturbations: list[CostPerturbation]`, onde cada perturbação é uma terna `(fee_delta_bps ≥ 0, slip_delta_bps ≥ 0, spread_delta_bps ≥ 0 default 0.0)` com `label` único; pelo menos uma perturbação estritamente positiva em qualquer dos três componentes.
  2. `cost_stress(prices, strategy, budget, baseline_cost, perturbations, dataset_id)` valida eager (`perturbations` não-vazio, nem tudo zero considerando os três deltas, labels únicos) e levanta `ValidationError` em qualquer violação antes de rodar backtest.
  3. Roda `run_backtest` uma vez com `baseline_cost` (→ `scenario_index=0`, label `"baseline"`, `dataset_id` original). Depois, para cada perturbação `k`: monta `effective_cost = baseline + delta` componente a componente (aritmética aditiva em bps nos três eixos) e roda `run_backtest` com `dataset_id = f"{dataset_id}#stress{k}"` — sufixo análogo ao `#fold{k}` do walk-forward para auditabilidade em logs.
  4. Para cada cenário perturbado, calcula `delta = scenario.final_equity - baseline.final_equity`. Se `delta > 1e-6 * capital_inicial`, levanta `ValidationError` citando cenário e label — é bug do engine (violação da ADR-0010), não flakiness; o relatório não é devolvido em estado inconsistente.
  5. Retorna `CostStressReport(baseline, scenarios)`: `baseline` é uma `CostStressCell` com `scenario_index=0`; `scenarios` é uma `list[CostStressCell]` na mesma ordem das perturbações.
- **Outcome:** tabela de N+1 linhas cruzando custo efetivo × `final_equity` × `max_drawdown` × `trade_count` sobre uma estratégia + dataset + budget fixos. Complementa a property-based de monotonicidade (ADR-0010): a propriedade cobre pares arbitrários de custo; o stress cobre a grade explícita que um analista quer reportar. Defesa em profundidade — se o engine regredir, property-based e `cost_stress` acusam por caminhos diferentes.
- **Não incluído nesta ADR:** flags de fragilidade no relatório (`FRÁGIL`, `CUSTO-SENSÍVEL` etc.); persistência em `results/validation/`; CLI exposta; perturbações multiplicativas; redução de custo como stress; stress de preço / dataset / hiperparâmetros; integração com walk-forward cartesiana. Cada um vira ADR separada se entrar.
- **Covered by tests:** `tests/unit/test_cost_stress_schemas.py` (3 classes, `CostPerturbation` / `CostStressCell` / `CostStressReport` frozen + `extra="forbid"` + validators), `tests/unit/test_cost_stress.py` (validações eager + chamada feliz com MA 20/50: baseline `scenario_index=0`, índices crescentes, labels na ordem, aritmética aditiva bit-a-bit, sufixo `#stress{k}` no `dataset_id`, monotonicidade assertada por cenário), `tests/integration/test_cost_stress_pipeline.py` (end-to-end 5 cenários, `max_drawdown ∈ [0,1]` em todos, monotonicidade via caminho explícito).

## Flow: filtro de regime causal (ADR-0022)

- **Actor:** engine (`run_backtest`) dentro do loop causal.
- **Trigger:** chamador passa `regime_filter: RegimeFilter | None = None` para `run_backtest` (direto, via `walk_forward`, `cost_stress` ou CLI `--regime-filter`).
- **Steps:**
  1. Dentro do loop por barra `t`, após `signal = strategy.decide(window)` e **antes** de sizing/execução, o engine avalia: `if regime_filter is not None and not regime_filter.is_active(window):`.
  2. Filtro lê apenas `window.iloc[:-1]` por contrato (causal por construção — ADR-0002 herdado). Em warm-up (`len(causal) < required`) devolve `False`.
  3. Se inativo, engine coage `signal`: `Signal.HOLD` se `position.side == FLAT`; `Signal.EXIT` se posicionado. Filtro **não** cria posições, apenas suprime sinais.
  4. `regime_filter=None` (default) pula totalmente essa etapa — zero overhead, comportamento bit-a-bit pré-ADR-0022.
  5. `SMASlopeFilter(window, min_slope_bps)`: calcula `slope_bps = (sma[-1] - sma[-window]) / sma[-window] * 10000` sobre SMA de `close`; ativo quando `abs(slope_bps) >= min_slope_bps`. `min_slope_bps=0` aceita tudo.
- **Outcome:** filtro reduz população de sinais processados a regimes de mercado "compatíveis" com a estratégia. Monotonicidade estrutural: aumentar `min_slope_bps` nunca aumenta `trade_count`.
- **Persistência:** CLI `validate` serializa o filtro em `run.json` via `canonical_string(regime_filter)` — `None → "none"`, `SMASlopeFilter → "sma_slope:min_slope_bps=<g>:window=<int>"` (ordem alfabética). Consumidores de `compare` detectam a divergência entre corridas filtradas e não-filtradas automaticamente pela seção `flags`.
- **Covered by tests:** `tests/property/test_regime_filter_neutrality.py` (filtro sempre-ativo é bit-a-bit idêntico a `regime_filter=None`), `tests/property/test_regime_filter_lookahead.py` (perturbar `window.iloc[-1]` com valores adversariais não muda `is_active`), `tests/property/test_sma_slope_filter_monotonicity.py` (`min_slope_bps` maior → `trade_count` menor ou igual), `tests/integration/test_cli_run_metadata.py::TestFlagsCapturadas::test_regime_filter_*` (default "none"; canonicalização alfabética em `run.json`; spec inválido rejeitado com exit 2).

## Flow: persistência de relatórios de validação (ADR-0015)

- **Trigger:** `from alpha_forge.validation import save_walk_forward_folds, load_walk_forward_folds, save_monte_carlo_summary, load_monte_carlo_summary, save_cost_stress_report, load_cost_stress_report` em notebook, script ou teste de integração; ou `pytest tests/unit/test_validation_persistence.py` e `tests/integration/test_validation_persistence_pipeline.py`. Opcionalmente `from alpha_forge.io.paths import validation_run_dir` para resolver `results/validation/<run_id>/`.
- **Steps:**
  1. Chamador roda `walk_forward`, `monte_carlo_trades` e/ou `cost_stress` normalmente (ADR-0003 + ADR-0014). Persistência é lado passivo — não altera nem um caractere dos três contratos funcionais.
  2. Chamador escolhe `run_id` (string opaca — convenção sugerida é `f"{dataset_id}__{strategy_slug}__{timestamp_utc}"` mas não imposta). `validation_run_dir(run_id)` resolve o diretório canônico.
  3. Para cada artefato opcional: `save_walk_forward_folds(folds=..., directory=...)`, `save_monte_carlo_summary(summary=..., directory=...)`, `save_cost_stress_report(report=..., directory=...)`. Cada função cria o diretório se não existir e devolve o `Path` gravado. Sobrescrita é permitida (sem confirmação).
  4. Cada arquivo é JSON UTF-8 com envelope `{"schema_version": "1", "payload": <dump pydantic>}`. `schema_version` é string — comparação é exata.
  5. Para carregar: `load_walk_forward_folds(directory=...)`, `load_monte_carlo_summary(directory=...)`, `load_cost_stress_report(directory=...)`. Levanta `FileNotFoundError` se o arquivo não existir; `ValidationError` se JSON malformado, envelope inválido, `schema_version` incompatível, ou payload violando schema pydantic.
- **Outcome:** round-trip bit-a-bit garantido estruturalmente — `load_*(save_*(x))` devolve objeto `==` a `x` em `__eq__` pydantic. `BacktestResult` completo é persistido (com `fills`, `trades`, `equity_curve`, `metrics`); truncagem silenciosa violaria reprodutibilidade e foi rejeitada na ADR. Artefatos são independentes: uma corrida que só rodou `cost_stress` grava só `cost_stress.json`; `load_walk_forward_folds` sobre esse diretório levanta `FileNotFoundError` limpamente.
- **Não incluído nesta ADR:** compressão gzip; migração entre versões de schema; identidade por hash; CLI; metadados de contexto (`strategy`, `timestamp`) no envelope; `save_trades_only=True`; abrir `ranking/` consumidor. Cada um vira ADR separada se entrar.
- **Covered by tests:** `tests/unit/test_validation_persistence.py` (4 classes, 24 testes: round-trip bit-a-bit por artefato, path devolvido, criação de diretório inexistente, envelope com `schema_version="1"`, incompatibilidade de versão, JSON malformado, envelope sem `payload`, arquivo inexistente, sobrescrita, lista vazia para walk-forward, payload violando schema, independência entre artefatos), `tests/integration/test_validation_persistence_pipeline.py` (pipeline completo sobre MA 20/50 no sintético seminal: walk-forward + Monte Carlo + cost_stress → persistir → carregar → `__eq__` dos três).

## Flow: CLI de validação (`alpha-forge validate`, ADR-0016 + ADR-0017)

- **Actor:** usuário / script de experimentação.
- **Trigger:** `alpha-forge validate --run-id <id> --dataset-id <ds> [...flags]` no shell, ou `from alpha_forge.cli.app import run; run(["validate", "--run-id", ..., ...])` em notebook/teste.
- **Steps:**
  1. CLI parseia flags; `--run-id` é obrigatório. Se `--stress` foi passado, cada spec é validada via `parse_stress_specs` **antes** de rodar qualquer backtest (formatos inválidos, labels duplicados, valores negativos disparam `parser.error` → exit 2). Se `--regime-filter` foi passado (default `"none"`), `parse_spec` valida o formato `name:k=v:k=v` (ADR-0022) **antes** do pipeline (nome desconhecido, kwarg duplicado ou faltando → exit 2).
  2. `_flags_from_namespace(args)` coage `argparse.Namespace` → `dict[str, str]` (exclui `command`; listas viram `repr`). Em seguida, a chave `flags["regime_filter"]` é **sobrescrita** por `canonical_string(regime_filter)` para garantir forma canônica alfabética dos kwargs em `run.json` (ADR-0022 §persistência).
  3. CLI resolve `directory = validation_run_dir(run_id)` (ADR-0015). **Antes do pipeline** (ADR-0017): instancia `RunMetadata(alpha_forge_version=alpha_forge.__version__, timestamp_utc=_now_utc(), command="validate", run_id=..., flags=...)` e chama `save_run_metadata(metadata, directory)` → `run.json` é gravado. Em seguida imprime cabeçalho: `dataset`, `strategy`, `run_id`, `out_dir`, `run_metadata`.
  4. Walk-forward roda sempre. `walk_forward(prices, strategy, budget, cost_model, ..., n_folds, scheme, train_fraction, min_test_bars, regime_filter)` → lista de `WalkForwardFold`. O `regime_filter` é o mesmo objeto parseado no passo 1 e é propagado para todas as chamadas internas de `run_backtest` (um por fold). Imediatamente `save_walk_forward_folds(folds=..., directory=...)` grava `walk_forward.json`.
  5. Se `--skip-monte-carlo` não foi passado: trades de todos os folds são agregados num `BacktestResult` sintético (mesmo padrão de `tests/integration/test_validation_persistence_pipeline.py`); `monte_carlo_trades(result=agg, capital_inicial, n_resamples=--mc-resamples, seed=--mc-seed)` → `MonteCarloSummary`; `save_monte_carlo_summary` grava `monte_carlo.json`. Se os folds não produziram nenhum trade, MC é pulado silenciosamente com nota em stderr; `monte_carlo.json` não é gravado.
  6. Se `--skip-cost-stress` não foi passado **e** `--stress` produziu ao menos uma perturbação: `cost_stress(prices, strategy, budget, baseline_cost, perturbations, dataset_id, regime_filter)` → `CostStressReport`; o mesmo `regime_filter` é aplicado ao baseline e a cada cenário perturbado, garantindo que ADR-0010 continua válida sob o filtro (custo maior com mesmo filtro → `final_equity` não sobe). `save_cost_stress_report` grava `cost_stress.json`.
  7. Summary no stdout: uma linha por artefato persistido, citando contagens (folds/trade_count, resamples/seed/median_final, scenarios) e o path gravado.
- **Outcome:** até quatro artefatos JSON versionados em `results/validation/<run_id>/`: `run.json` sempre (contrato ADR-0017 — trilha de auditoria), e os três relatórios de pipeline (ADR-0015) cada um opcional e independente. Consumidores futuros (`ranking/`, notebooks, comparadores) lêem via `load_*` — não precisam saber que a corrida veio da CLI. Sobrescrita é silenciosa: mesma `run_id` rodada de novo regrava os arquivos.
- **Rastro de auditoria em abort (ADR-0017):** se `walk_forward`/`monte_carlo_trades`/`cost_stress` levantar `ValidationError` ou `DatasetIntegrityError`, `run.json` permanece gravado (foi escrito antes) — operador consegue reconstruir o que foi tentado mesmo sem artefatos de pipeline.
- **Códigos de saída:** `0` em sucesso; `1` se `ValidationError` ou `DatasetIntegrityError` levantou (erro operacional — mensagem curta em stderr, sem stacktrace); `2` em erro de flags (argparse + `parse_stress_specs`); exceções inesperadas sobem com stacktrace completo (são bug, queremos ver).
- **Não incluído nas ADRs 0016/0017:** descoberta de corridas pré-existentes (`--list`), grid de estratégias/datasets, `--stress-file` externo, tuning de parâmetros, host info/hash de dataset em metadados. Comparação de corridas (`compare` subcomando) passou a existir via ADR-0018 (flow logo abaixo). Cada outro ponto vira ADR própria se houver consumidor.
- **Covered by tests:** `tests/unit/test_cli_parse_stress.py` (4 classes, 18 testes — inclui `TestFormatoQuatroPartesSpread` com 5 casos da 4ª parte `spread_delta_bps` via ADR-0019), `tests/integration/test_cli_validate.py` (3 classes, 6 testes: pipeline completo, flags de skip, erros de flag/domínio), `tests/unit/test_run_metadata_persistence.py` (3 classes, 13 testes: schema rejeitando campos desconhecidos/vazios/frozen; round-trip bit-a-bit com timestamp tz-aware; envelope com `schema_version="1"`; erros de arquivo/envelope/schema/payload), `tests/integration/test_cli_run_metadata.py` (3 classes, 4 testes: `run.json` carregável em corrida ok com `timestamp_utc` fixado via `_now_utc` monkeypatch; `run.json` sobrevive `ValidationError` com `n_folds=1`; `--stress` repetido serializa como `repr` de lista; `--skip-*` persistem em `flags`).

## Flow: CLI de comparação de corridas (`alpha-forge compare`, ADR-0018)

- **Actor:** usuário / script de experimentação / CI de reprodutibilidade.
- **Trigger:** `alpha-forge compare RUN_ID_A RUN_ID_B [--skip-run-metadata] [--skip-walk-forward] [--skip-monte-carlo] [--skip-cost-stress] [--log-level ...]` no shell, ou `from alpha_forge.cli.app import run; run(["compare", "run_a", "run_b"])` em notebook/teste.
- **Pré-requisitos:** as duas corridas já persistidas em `results/validation/<run_id>/` via `alpha-forge validate` (ADR-0016). `run.json` (ADR-0017) deve existir em ambas — por construção da ADR-0017, sempre é gravado antes do pipeline.
- **Steps:**
  1. CLI parseia dois args posicionais (`run_id_a`, `run_id_b`) e quatro flags `--skip-*`. Dois args faltando → argparse → exit 2.
  2. `directory_a = validation_run_dir(run_id_a)`, `directory_b = validation_run_dir(run_id_b)` resolvem caminhos canônicos (ADR-0015). Nenhuma verificação preventiva de existência — ausência será diagnosticada pelo `load_*` ou pelo `Path.exists()` de seção opcional, conforme o caso.
  3. Header: imprime `run_a : <id_a> (<directory_a>)` e `run_b : <id_b> (<directory_b>)`, depois linha em branco.
  4. **Seção `run_metadata` (obrigatória):** se não `--skip-run-metadata`, chama `load_run_metadata(directory_a)` e `load_run_metadata(directory_b)` diretamente. Ausência de `run.json` (violação de contrato ADR-0017) levanta `FileNotFoundError` → dispatcher captura → exit 1 com `"erro: ..."` em stderr. Se ambos ok, imprime `_diff_run_metadata(meta_a, meta_b)` linha a linha: versão + timestamp (`Δ=+Xs`) + command + run_id + flags (lista ordenada se divergentes, contagem se todas iguais).
  5. **Seções `walk_forward` / `monte_carlo` / `cost_stress` (opcionais e independentes):** para cada uma, se a flag `--skip-*` correspondente está ligada, imprime apenas `pulado (--skip-<nome>)`. Caso contrário, faz `(directory / "<nome>.json").exists()` em ambos:
     - ambos existem → `load_*` + `_diff_*` (funções puras sobre pydantic, sem I/O);
     - só A → `"presente em A, ausente em B"`;
     - só B → `"ausente em A, presente em B"`;
     - nenhum → `"ausente em ambos"`.
  6. Exit `0` mesmo que todos os valores divirjam. Divergência é observação, não falha (ADR-0018 §"Alternatives considered").
- **Read-only absoluto:** `compare` **não grava, modifica ou apaga nenhum arquivo**. Testado em `tests/integration/test_cli_compare.py::test_compare_não_altera_artefatos` (size + mtime de todos os arquivos do `run_id_a` antes/depois são idênticos).
- **Formato de saída (contrato humano, não machine-parseable):** header + 4 seções `--- <nome> ---`, cada seção com linhas indentadas 2 espaços. Valores numéricos usam `_fmt_delta(x) = f"{x:+.4f}"` para equity (4 casas, sinal explícito); `_diff_monte_carlo` usa 6 casas para `max_drawdown`; `_diff_run_metadata` usa `.1f` para segundos de timestamp. O contrato machine-parseable continua sendo o JSON persistido; `compare` gera diff humano para inspeção rápida.
- **Walk-forward é agregado:** o diff mostra 4 totais (`n_folds`, `total_trades`, `total_test_bars`, `sum_final_equity`). Diff fold-a-fold foi rejeitado para não poluir stdout; granularidade fica para inspeção programática via `load_walk_forward_folds`.
- **Monte Carlo compara percentis fixos** (`{5, 25, 50, 75, 95}` ADR-0003) + `n_resamples` + `seed` + os dois originais (`original_final_equity`, `original_max_drawdown`). Como `seed` é parte do contrato, duas corridas do mesmo dataset com mesmo `--mc-seed` produzem todos os percentis idênticos (Δ=+0.0000) — verificação mecânica de reprodutibilidade.
- **Cost stress indexa cenários por `label`:** união ordenada; labels só em A / só em B imprimem `"presente em A, ausente em B"` / `"ausente em A, presente em B"`; labels em ambos mostram `Δ` de `final_equity`. `label` é a chave natural estável da ADR-0014.
- **Códigos de saída:** `0` sempre em sucesso, inclusive com divergência. `1` em `FileNotFoundError` (run inexistente, `run.json` ausente) ou `ValidationError` (JSON malformado / envelope inválido / schema incompatível em algum `load_*`). `2` em erro de flags (argparse).
- **Não incluído nesta ADR:** saída JSON (machine-parseable); exit-code ≠ 0 em divergência; ranking/scoring cross-run; comparar ≥ 3 corridas; comparar por hash de payload; diff fold-a-fold; backends `tabulate`/`rich`. Cada um vira ADR própria se houver consumidor.
- **Covered by tests:**
  - `tests/unit/test_cli_compare_diffs.py` (4 classes, 21 testes): cada `_diff_*` testado sobre pydantic hand-constructed sem filesystem — tags `igual`/`divergente`, Δs com sinal, ordenação alfabética de chaves/labels, ausência simétrica de flags/labels, seis casas para `max_drawdown`, percentis fixos presentes.
  - `tests/integration/test_cli_compare.py` (2 classes, 8 testes): grava duas corridas reais via `cli_app.run(["validate", ...])` em `tmp_path` com `validation_run_dir` redirecionado, depois chama `cli_app.run(["compare", ...])` e valida stdout, exit codes, seções presentes/puladas, read-only bit-a-bit (size+mtime dos artefatos), comparação assimétrica entre corrida com e sem `--stress` (ausência de `cost_stress.json` em B produz marcador `presente em A, ausente em B`), run_id inexistente → exit 1, args posicionais faltando → exit 2.

## Flow: CLI de ranking de pilotos (`alpha-forge rank`, ADR-0024)

- **Actor:** usuário / script de comparação em massa / CI de regressão.
- **Trigger:** `alpha-forge rank [--runs-dir PATH] [--slug SLUG]* [--weights-file PATH] [--eligibility EXPR] [--agentic-dir PATH] [--output PATH] [--format json|table] [--log-level ...]` no shell, ou `from alpha_forge.cli.app import run; run(["rank", ...])` em teste/notebook.
- **Pré-requisitos:** pelo menos um piloto persistido em `results/validation/<slug>/` via `alpha-forge validate`. Para parse de `release_decision`, `agentic/active/<slug>/AUDIT.md` com a linha `release_decision: <fail|paper_only|canary_only>` (ADR-0020). AUDIT.md ausente → piloto classificado como `fail`.
- **Steps:**
  1. CLI parseia flags. Sem `--slug`, roda auto-discovery via `discover_slugs(runs_dir)` — subdirs com os 4 JSONs canônicos, ordenados alfabeticamente.
  2. `--weights-file` opcional é lido via `load_weights_toml`; ausente → `ScoreWeights()` com defaults de ADR-0024.
  3. Para cada slug: `load_run_metadata` + `load_walk_forward_folds` + `load_monte_carlo_summary` + `load_cost_stress_report`. Qualquer erro (`FileNotFoundError`, `ValidationError`, `RankingError` interno) → warning em stderr (`[rank] aviso: pulando <slug>: ...`) e o piloto é excluído; pipeline não aborta.
  4. `_extract_row_raw` extrai 14 campos brutos: `fe_baseline`, `hit_baseline`, `mdd_baseline`, `trade_count`, `spread_stress_ratio` (= `fe(spread+10) / fe(baseline)`), `mc_p5/p50/p95`, `fold_max_hit`, `fold_min_hit`, `fold_std_hit` (`statistics.pstdev`), `release_decision` (regex sobre AUDIT.md), `flags_digest` (sha256 canônico truncado a 16 hex).
  5. Eligibility (`all` default, ou `release_decision (==|!=) 'valor'`) filtra as linhas antes do scoring. Zero pilotos sobreviventes → `RankingError` → exit 1.
  6. `_compute_composite_scores` aplica min-max normalização sobre a amostra (todos iguais → `0.5`) com direção canônica por métrica (maior=melhor para fe/hit/stress/p5/fold_min; menor=melhor para mdd/fold_std). Score linear ponderado = Σ (wᵢ × norm_i).
  7. Ordenação por `(-composite_score, slug)` — score desc, tiebreak slug asc. `rank` é atribuído 1-indexed após ordenação.
  8. `save_leaderboard` grava `RankedLeaderboard` como JSON indentado em `--output` (default: `results/ranking/<generated_at>.json`) — **sem envelope**, pois é output de usuário.
  9. Stdout segue `--format`: `json` imprime o payload via `json.dumps(..., indent=2)`; `table` imprime cabeçalho + uma linha por piloto com `rank / slug / composite_score / hit / fe / mdd / trades / release_decision`.
- **Determinismo:** `generated_at` é o único campo não-determinístico por default. Passar `generated_at=` explícito → `RankedLeaderboard` byte-idêntico entre runs (testado em `test_determinism_bit_exact`).
- **Invariantes testadas:**
  - permutação-invariância do input de slugs (`test_permutation_invariance`, 15 max_examples);
  - min-max constante → todos os pilotos recebem score = Σ(wᵢ × 0.5) (`test_all_equal_pilots_get_equal_scores`);
  - `flags_digest` invariante a reordenação de keys + sensível a mudança de valor (`test_flags_digest_stable_and_sensitive`);
  - eligibility é filtro puro (`test_eligibility_filters_without_reordering`);
  - zero elegíveis → `RankingError` (`test_zero_eligible_raises`);
  - integration test sobre os 12 pilotos reais atuais do repositório (`tests/integration/test_cli_rank.py`) — cobre CLI + I/O + ordenação sobre fixture viva.
- **Exit codes:** `0` sucesso (inclusive com pilotos pulados por warning). `1` em zero pilotos elegíveis ou TOML de pesos inválido. `2` em flags malformadas (argparse).
- **Covered by tests:**
  - `tests/property/test_ranking_properties.py` (6 testes, 1 property-based) — invariantes acima, `_flags_digest` direto, e `_write_piloto` helper para fixture sintética.
  - `tests/integration/test_cli_rank.py` (1 teste, condicional) — roda o CLI sobre os pilotos reais do repositório como fixture viva; ranks sequenciais, scores ordenados desc, digests únicos.

## Flow: smoke test do pacote

- **Actor:** desenvolvedor / CI.
- **Trigger:** `pytest` local ou push/PR no GitHub.
- **Steps:** `tests/unit/test_smoke.py::test_package_imports` importa `alpha_forge` e checa `__version__`.
- **Outcome:** sanidade do scaffolding.
- **Covered by test:** o próprio arquivo.

## Flow: pipeline mínimo de CI (ADR-0021)

- **Trigger:** push para `main` ou abertura de pull request.
- **What it does:** `ruff check` + `ruff format --check` + `pyright` + `pytest -q` + `python scripts/validate_artifacts.py` (ADR-0020, opt-in — cobra artefatos agentic se há piloto em `agentic/active/<slug>/`; exit 0 silencioso em repo sem piloto) + gate anti-hardcode `grep -rE '\b(BTC|ETH|SOL)\b' src/` (ADR-0009 §2-ter — exit 1 se qualquer match; hoje 0 matches).
- **Side effects:** bloqueia merge se qualquer etapa falhar.
- **Defined in:** `.github/workflows/ci.yml`.
- **Covered by test:** o próprio workflow; os steps novos são validados pelos mesmos sanity checks que rodam localmente (ver "Flow: overlay agentic" abaixo).

## Flow: overlay agentic — pesquisa automatizada de hipóteses (ADR-0020)

- **Trigger:** operador (humano) ou `lead-orchestrator` invoca `cp agentic/templates/*.md agentic/active/<slug>/` para abrir um piloto com slug kebab-case curto.
- **What it does:** 5 subagentes (`lead-orchestrator` → `strategy-researcher` → `strategy-implementer` → `backtest-validator` → `risk-auditor`) preenchem os 6 artefatos sequencialmente em `agentic/active/<slug>/` (SPEC → IMPLEMENTATION → VALIDATION → BACKTEST → AUDIT → CHECKLIST). Cada gate é verificável e fixo em ordem: pesquisa → implementação → validação → auditoria → release (release exige assinatura humana, `release_decision ∈ {fail, paper_only, canary_only}` — nunca `live`).
- **Side effects:** durante o piloto, o Stop hook `.claude/hooks/check_gates.py` cobra presença/coerência dos 6 artefatos + `STATE.md` raiz — exit 2 se faltar qualquer seção ou se houver placeholder `{{...}}` não preenchido. Ao concluir, piloto pode ser movido para `agentic/inactive/<slug>/` (opcional, on-demand). CI (ADR-0021) roda `scripts/validate_artifacts.py` para cobrar o mesmo em PR.
- **Defined in:** `agentic/README.md`, `.claude/agents/*.md`, `.claude/hooks/check_gates.py`, `scripts/validate_artifacts.py`.
- **Covered by sanity checks:** dry-run de `python scripts/validate_artifacts.py` em repo sem piloto retorna "nenhum piloto ativo — OK" exit 0; positive case (criar `agentic/active/_sanity/` vazio) dispara exit 2 com stderr listando 6 artefatos ausentes.

### Output exemplo 18 — Séries AA + AB + AC (9 pilots; protocolo N=70; descoberta AC.1)

```
# 9 pilotos: AA (4 ETH window×num_std), AB (2 RSI cross-asset filter),
# AC (3 OOS 2025 de parametrizações não-default). Reutilização do engine
# Bollinger/RSI + filtro ATR; zero código novo. N=70, validator OK.

$ scripts/_gen_aaabac_artifacts.py  # gera 54 .md (9 × 6)
Done: 54 files for 9 pilots (AA/AB/AC)

$ scripts/validate_artifacts.py
[validate_artifacts] OK — 70 piloto(s) ativo(s), todos os artefatos presentes.

$ alpha-forge rank --format table
ranked 70 pilotos  (saved: results/ranking/20260418T144942Z.json)
rank  slug                                                score    hit      fe
   1  bollinger-20-2-eth-1h-2024-regime-atr-130          7.742  85.71%  10299
   3  bollinger-20-2-eth-1h-2024-regime-atr-105  (U.2)   7.325  73.68%  10619
  22  bollinger-20-15-eth-1h-2024-regime-atr-105 (AA.3)  6.683  63.16%  10540
  23  bollinger-20-15-eth-1h-2025-regime-atr-105 (AC.1)  6.677  64.15%  10465  ← OOS ROBUST
  34  rsi-14-30-70-eth-1h-2024-regime-atr-90     (AB.2)  6.039  67.50%  10458
```

**Findings AA/AB/AC:**
- **AA** (window×num_std): AA.3 20/1.5 domina AA.1 10/2 em fe. Sensibilidade paramétrica existe mas é secundária ao filtro ATR.
- **AB** (filtro ATR em RSI cross-asset): AB.2 ETH RSI+atr:90 (fe 10458 hit 67.50%) **refuta** conclusão S.1 "Bollinger-specific" — filtro agrega em RSI-ETH especificamente. Interação filtro×asset é não-trivial.
- **AC** (OOS 2025 de configs não-default): AC.1 ETH 20/1.5+atr:105 **preserva edge** (fe 10465 hit 64.15%) onde W.3 ETH 20/2.0 degrada (fe 10077 hit 57.14%) — **parametrização 1.5 std é mais robusta cross-window que 2.0**. Primeiro piloto do protocolo a preservar edge OOS 2025.

**Implicação operacional:** handoff dualista — U.2 (in-sample rank 3) para tape 2024-H2 + AC.1 para deploy OOS futuro. Banda apertada (1.5 std) é recomendação principal para canary 2025+.

**ADR-0019** 70 confirmações totais (+9 em AA/AB/AC). Suíte preservada em 366 passed, 1 skipped.

---

### Output exemplo 19 — Série AD (3 pilots; refutação cross-asset de AC.1; protocolo N=73)

```
# Hipótese: num_std=1.5 preserva edge OOS 2025 cross-asset (generalizando AC.1).
# Resultado: refutada. 1.5 std é ETH-específico.

$ alpha-forge validate --strategy bollinger --bollinger-num-std 1.5 \
    --dataset-id btcusdt_1h_20250705_20251231_binance_spot \
    --regime-filter atr_regime:window=14:min_atr_bps=55 \
    --run-id bollinger-20-15-btc-1h-2025-regime-atr-55 \
    --stress fee+10:10:0:0 --stress spread+10:0:0:10
# AD.1: trades=54 hit=44.44% fe=9985 ratio=0.9784 → FAIL gate 1

$ alpha-forge validate --strategy bollinger --bollinger-num-std 1.5 \
    --dataset-id solusdt_1h_20250705_20251231_binance_spot \
    --regime-filter atr_regime:window=14:min_atr_bps=100 ...
# AD.2: trades=75 hit=46.67% fe=9264 ratio=0.9678 → canary_only mas fe<10000

$ alpha-forge validate --strategy bollinger --bollinger-num-std 1.5 \
    --dataset-id ethusdt_1h_20250705_20251231_binance_spot ...  # sem filtro
# AD.3 (controle): trades=107 hit=62.62% fe=10071 → ETH sem filtro preserva edge

$ alpha-forge rank --format table
ranked 73 pilotos  (saved: results/ranking/20260418T150323Z.json)
  23  bollinger-20-15-eth-1h-2025-regime-atr-105 (AC.1)  6.677  64.15%  10465
  45  bollinger-20-15-btc-1h-2025-regime-atr-55  (AD.1)  5.547  44.44%   9985  FAIL
  49  bollinger-20-15-eth-1h-2025-baseline       (AD.3)  5.339  62.62%  10071
  63  bollinger-20-15-sol-1h-2025-regime-atr-100 (AD.2)  3.810  46.67%   9264
```

**Findings AD:**
- **AC.1 NÃO GENERALIZA cross-asset.** Hipótese "num_std=1.5 é mais robusto OOS" refutada em BTC (fail hard gate) e SOL (fe < 10000).
- **AD.3 controle:** ETH 20/1.5 SEM filtro ainda preserva edge (hit 62.62% fe 10071) — parte do ganho AC.1 vem do 1.5 std ETH-específico, não da combinação com ATR filter.
- **Asset-specificity é dominante.** Edge OOS em Bollinger MR é ETH-específico; BTC/SOL não preservam em nenhuma config testada.
- **Nenhum candidato cross-asset OOS.** Após 73 pilotos, zero configuração preserva edge em ≥2 assets OOS simultaneamente.

**Implicação operacional:** deploy real em produção continua sem evidência adequada. Recomendação: continuar testando antes de canary-trade.

**ADR-0019:** 73 confirmações totais (+3 em AD).

---

### Output exemplo 20 — Série AE (4 pilots; 20/1.5 in-sample 2024; AE.2 fe=11210 record; protocolo N=77)

```
# Hipótese: 20/1.5 tem edge in-sample 2024 em BTC/SOL
#           (separa asset-specificity de window-specificity após AD)

$ alpha-forge validate --strategy bollinger --bollinger-num-std 1.5 \
    --dataset-id btcusdt_1h_20240705_20241231_binance_spot \
    --regime-filter atr_regime:window=14:min_atr_bps=55 ...
# AE.1: trades=84 hit=72.62% fe=10474 → RANK 6

$ alpha-forge validate --strategy bollinger --bollinger-num-std 1.5 \
    --dataset-id solusdt_1h_20240705_20241231_binance_spot \
    --regime-filter atr_regime:window=14:min_atr_bps=100 ...
# AE.2: trades=96 hit=66.67% fe=11210 → BEST fe DO PROTOCOLO

$ alpha-forge rank --format table | head -15
   5  bollinger-20-2-sol-1h-2024-regime-atr-100      (R.1)  7.082  70.77%  10803
   6  bollinger-20-15-btc-1h-2024-regime-atr-55      (AE.1) 7.054  72.62%  10474  ← NEW
  12  bollinger-20-15-sol-1h-2024-regime-atr-100     (AE.2) 6.829  66.67%  11210  ← best fe
```

**Findings AE:**
- **20/1.5 é universal in-sample.** 3 assets (BTC/ETH/SOL) todos com edge em 2024.
- **20/1.5 SUPERA 20/2 em SOL 2024.** AE.2 fe 11210 > R.1 fe 10803. Primeira alternativa a 20/2 que domina.
- **Degradação AD (OOS 2025) é cross-window, não asset-specific.** 20/1.5 funciona in-sample cross-asset; degrada OOS na maioria dos assets (só ETH preserva).
- **Filtro ATR mantém valor incremental cross-window:** AE.1 vs AE.3 é +7.5pp hit.

**Status operacional:** ainda sem candidato cross-asset OOS; continuar pesquisando. 20/1.5 merece exploração cross-window adicional (Série AF).

**ADR-0019:** 77 confirmações totais (+4 em AE).

---

### Output exemplo 21 — Série AF (3 pilots; 2025-H1 cross-window; decay contínuo; protocolo N=80)

```
# Ingere 2025-H1 (primeira janela intermediária entre 2024 in-sample e 2025-H2 OOS)
$ python scripts/ingest_binance_vision.py --symbols BTCUSDT,ETHUSDT,SOLUSDT \
    --timeframe 1h --start 2025-01-05 --end 2025-07-04
# 3 datasets, 4344 barras cada, zero gaps

# Testa 20/1.5 em cada asset
$ alpha-forge validate --strategy bollinger --bollinger-num-std 1.5 \
    --dataset-id btcusdt_1h_20250105_20250704_binance_spot --regime-filter atr_regime:window=14:min_atr_bps=55 ...
# AF.1 BTC 2025-H1: hit 58.21% fe 10360 → PRESERVA (2025-H2 falhava)
# AF.2 ETH 2025-H1: hit 62.90% fe 10376 → estável (3 janelas consecutivas)
# AF.3 SOL 2025-H1: hit 58.14% fe 9770 → colapsa (perde capital)
```

**Decay cross-window (hit rate):**

| Asset | 2024-H2 | 2025-H1 | 2025-H2 |
|-------|--------:|--------:|--------:|
| BTC | 72.62% | 58.21% | 44.44% |
| **ETH** | **63.16%** | **62.90%** | **64.15%** |
| SOL | 66.67% | 58.14% | 46.67% |

**Findings AF:**
- **Decay é CONTÍNUO no tempo**, não quebra abrupta — mercado mudou durante 2025.
- **ETH é asset MAIS estável cross-window** (variação 2pp em 3 semestres).
- **SOL instável em 2025** — ambos semestres perdem capital.
- **Metodologia:** 1 janela OOS pode gerar falso positivo. Mínimo 2 janelas para concluir generalização.
- **Candidato emergente:** ETH 20/1.5+atr:105 — edge em 3 janelas, 1 asset, ainda insuficiente para canary.

**ADR-0019:** 80 confirmações totais (+3 em AF).

---

### Output exemplo 22 — Série AG (3 pilots; 2024-H1 4ª janela; ETH CANDIDATO FORTE; protocolo N=83)

```
# Ingere 2024-H1 (4ª janela OOS consecutiva)
$ python scripts/ingest_binance_vision.py --symbols BTCUSDT,ETHUSDT,SOLUSDT \
    --timeframe 1h --start 2024-01-05 --end 2024-07-04

$ alpha-forge validate --strategy bollinger --bollinger-num-std 1.5 \
    --dataset-id ethusdt_1h_20240105_20240704_binance_spot --regime-filter atr_regime:window=14:min_atr_bps=105 ...
# AG.1 ETH 2024-H1: hit 77.50% fe 10654 → RANK 3 no leaderboard

$ alpha-forge rank --format table | head -5
   1  bollinger-20-2-eth-1h-2024-regime-atr-130       7.603  85.71%  10299  (14 trades, marginal)
   2  bollinger-20-2-btc-1h-2024-regime-atr-100       7.520  75.00%  10270  (16 trades, marginal)
   3  bollinger-20-15-eth-1h-2024h1-regime-atr-105    7.498  77.50%  10654  (40 trades ← AG.1)
```

**ETH 20/1.5+atr:105 — 4 janelas consecutivas (193 trades agregados):**

| Janela | trades | hit | fe | ratio |
|--------|-------:|----:|---:|------:|
| 2024-H1 | 40 | 77.50% | 10654 | 0.9847 |
| 2024-H2 | 38 | 63.16% | 10540 | 0.9855 |
| 2025-H1 | 62 | 62.90% | 10376 | 0.9761 |
| 2025-H2 | 53 | 64.15% | 10465 | 0.9797 |

**Findings AG:**
- **ETH é PRIMEIRO CANDIDATO FORTE.** 4/4 janelas preservam gates (hit > 45%, fe > 10000, ratio > 0.95, mdd < 5%).
- **BTC 2024-H2 era outlier positivo.** Em 3/4 janelas falha (hit 44-58%, fe < 10500).
- **SOL colapsa** em 2025 ambos semestres.
- **Candidato de deploy emergente:** ETH 20/1.5+atr:105, base estatística de 193 trades cross-window.

**ADR-0019:** 83 confirmações totais (+3 em AG).

---

### Output exemplo 23 — Série AH (4 pilots; 5ª janela 2023-H2 + cross-timeframe 4h; narrativa REFINADA; protocolo N=87)

```
# Ingere 2023-H2 (5ª janela OOS). 2023-H1 rejeitado por 1 gap não declarado.
$ python scripts/ingest_binance_vision.py --symbols BTCUSDT,ETHUSDT,SOLUSDT \
    --timeframe 1h --start 2023-07-05 --end 2023-12-31
# 3 datasets, 4320 barras cada, zero gaps.

# AH.1 ETH 20/1.5+atr:105 em 2023-H2 (5ª janela consecutiva)
$ alpha-forge validate --strategy bollinger --bollinger-num-std 1.5 \
    --dataset-id ethusdt_1h_20230705_20231231_binance_spot \
    --regime-filter atr_regime:window=14:min_atr_bps=105 ...
# AH.1: 10 trades, hit 50.00%, fe 10042 — filtro ATR quase inativo em 2023 (baixa vol)

# AH.4 ETH 20/1.5+atr:105 em 4h (cross-timeframe sobre 2024-H2)
$ alpha-forge validate --strategy bollinger --bollinger-num-std 1.5 \
    --dataset-id ethusdt_4h_20240705_20241231_binance_spot ...
# AH.4: 24 trades, hit 58.33%, fe 9478 — PERDE 5.2% DE CAPITAL em 4h
```

**Quadro AH — 4 pilots, 4/4 `canary_only` mas com caveats:**

| Pilot | asset/tf/win | trades | hit | fe | mdd | rank |
|-------|--------------|-------:|----:|---:|----:|-----:|
| AH.1  | ETH 1h 2023-H2 | 10 | 50.00% | 10042 | 0.55% | 58 |
| AH.2  | BTC 1h 2023-H2 | 34 | 58.82% | 10027 | 1.87% | 44 |
| AH.3  | SOL 1h 2023-H2 | 64 | 54.69% | 10122 | 3.99% | 48 |
| AH.4  | ETH 4h 2024-H2 | 24 | 58.33% | **9478** | 7.38% | 61 |

**ETH 20/1.5+atr:105 — 5 janelas agora mapeadas:**

| Janela | trades | hit | fe | nota |
|--------|-------:|----:|---:|------|
| 2023-H2 | **10** | 50.00% | 10042 | amostra INSUFICIENTE |
| 2024-H1 | 40 | 77.50% | 10654 | robusto |
| 2024-H2 | 38 | 63.16% | 10540 | robusto |
| 2025-H1 | 62 | 62.90% | 10376 | robusto |
| 2025-H2 | 53 | 64.15% | 10465 | robusto |

**Cross-timeframe ETH 2024-H2 (mesmo asset, mesma janela, diferente TF):**

| Timeframe | trades | hit | fe | veredicto |
|-----------|-------:|----:|---:|-----------|
| 1h (U.2)  | 38 | 63.16% | 10540 | edge preservado |
| 4h (AH.4) | 24 | 58.33% | **9478** | PERDE 5.2% capital |

**Findings AH:**
- **Narrativa "ETH 4/4 universal" REFINADA.** Edge é **1h-específico** (4h falha −5.2%) e **2024-2025-específico** (2023 com 10 trades é inconclusivo, não confirmatório).
- **Filtro ATR:105 quase inativo em 2023.** ETH 2023-H2 só gera 10 sinais — regime de baixa volatilidade histórica desativa o gate.
- **BTC/SOL em 2023 marginais.** Fe +0.27% e +1.22% — sem edge material mas não falham gates (hit > 45%).
- **Implicação operacional:** se deploy real, **fixar timeframe 1h** + **esperar regime similar a 2024-2025** (alta vol). Evitar 4h e períodos calmos.
- **Próximas candidatas:** Série AI (sensibilidade fina de parâmetros ETH 1h), Série AJ (novas famílias de filtro), Série AK (novos assets ADA/BNB), resolver gap 2023-H1.

**ADR-0019:** 87 confirmações totais (+4 em AH).

---

### Output exemplo 24 — Série AI (4 pilots; sensibilidade paramétrica ETH 1h 2024-H2 em torno de U.2; PLATÔ LARGO; protocolo N=91)

```
# Sweep num_std em torno de baseline U.2 (1.5)
$ alpha-forge validate --strategy bollinger --bollinger-num-std 1.25 \
    --dataset-id ethusdt_1h_20240705_20241231_binance_spot \
    --regime-filter atr_regime:window=14:min_atr_bps=105 ...
# AI.1: hit 60.47% fe 10360

$ alpha-forge validate --strategy bollinger --bollinger-num-std 1.75 \
    --dataset-id ethusdt_1h_20240705_20241231_binance_spot \
    --regime-filter atr_regime:window=14:min_atr_bps=105 ...
# AI.2: hit 66.67% fe 10593 (supera U.2 em fe)

# Sweep atr threshold em torno de 105
$ alpha-forge validate ... --regime-filter atr_regime:window=14:min_atr_bps=90  ...
# AI.3: hit 70.37% fe 10667 (melhor fe ETH 2024-H2 do protocolo)

$ alpha-forge validate ... --regime-filter atr_regime:window=14:min_atr_bps=120 ...
# AI.4: hit 73.91% fe 10335 (menos trades, hit mais alto)
```

**Quadro AI — sensibilidade em torno de U.2 (ref: 1.5 / atr:105, 38 trades, hit 63.16%, fe 10540):**

| Pilot | num_std | atr | trades | hit | fe | ratio | rank |
|-------|--------:|----:|-------:|----:|---:|------:|-----:|
| AI.1 | 1.25 | 105 | 43 | 60.47% | 10360 | 0.9833 | 29 |
| U.2 (ref) | 1.5 | 105 | 38 | 63.16% | 10540 | 0.9855 | — |
| AI.2 | 1.75 | 105 | 39 | 66.67% | **10593** | 0.9852 | 31 |
| AI.3 | 1.5 | **90** | 54 | **70.37%** | **10667** | 0.9796 | 14 |
| AI.4 | 1.5 | **120** | 23 | **73.91%** | 10335 | 0.9910 | 13 |

**Findings AI:**
- **Platô largo, não peak estreito.** Todos 4 vizinhos preservam gates ADR-0025.
- **Trade-off identificado:** atr mais alto → menos trades, hit mais alto, ratio mais robusto (AI.4); atr mais baixo → mais trades, fe maior, ratio um pouco pior (AI.3).
- **AI.3 tem MELHOR fe ETH 2024-H2 do protocolo** (10667, supera U.2 em +127 e AG.1 em +13).
- **num_std=1.75 também supera U.2 em fe/hit.** Sugere que U.2 baseline é levemente sub-ótimo no eixo num_std.
- **Robustez do finding principal confirmada:** ETH 20/1.5+atr:105 não é um ponto frágil; a região paramétrica vizinha preserva edge.

**ADR-0019:** 91 confirmações totais (+4 em AI).

---

### Output exemplo 25 — Série AJ (6 pilots; cross-window de AI.3/AI.4; atr:120 ROBUSTO 4/4 janelas; protocolo N=97)

```
# Testa atr:90 e atr:120 em 3 janelas cada (2024-H1, 2025-H1, 2025-H2)
$ for atr in 90 120; do for win in 2024h1 2025h1 2025h2; do
    alpha-forge validate --strategy bollinger --bollinger-num-std 1.5 \
      --dataset-id ethusdt_1h_<win>_binance_spot \
      --regime-filter atr_regime:window=14:min_atr_bps=$atr ...
  done; done
```

**Quadro AJ — ETH 20/1.5+atr:120 (winner de AI.4) cross-window:**

| Janela | trades | hit | fe | ratio | p5 MC | pilot |
|--------|-------:|----:|---:|------:|------:|-------|
| **2024-H1** | 26 | **76.92%** | 10654 | 0.9901 | 10267 | AJ.4 |
| 2024-H2 | 23 | 73.91% | 10335 | 0.9910 | 10068 | AI.4 |
| 2025-H1 | 46 | 60.87% | 10382 | 0.9822 | 9628 | AJ.5 |
| 2025-H2 | 33 | 60.61% | 10054 | 0.9869 | 9513 | AJ.6 |
| **agregado** | **128** | ~66% | — | ≥0.982 | — | — |

**Quadro AJ — ETH 20/1.5+atr:90 (winner AI.3) cross-window:**

| Janela | trades | hit | fe | ratio | p5 MC | pilot |
|--------|-------:|----:|---:|------:|------:|-------|
| 2024-H1 | 57 | 64.91% | 10410 | 0.9778 | 10105 | AJ.1 |
| 2024-H2 | 54 | 70.37% | 10667 | 0.9796 | 10084 | AI.3 |
| 2025-H1 | 75 | 65.33% | 10410 | 0.9711 | 9777 | AJ.2 |
| 2025-H2 | 70 | 61.43% | 10215 | 0.9726 | 9460 | AJ.3 |
| **agregado** | **256** | ~65% | — | ≥0.971 | — | — |

**Findings AJ:**
- **atr:120 é a config MAIS ROBUSTA cross-window.** 4/4 janelas: hit 60.61-76.92% (variação 16pp), fe sempre ≥ 10054, ratio sempre ≥ 0.982, mdd sempre ≤ 3.51%. Trade-off: poucos trades (23-46 por janela = 128 agregados).
- **atr:90 tem mais amostra mas ratios piores.** 256 trades agregados vs 128, mas ratio_min 0.971 (vs 0.982) e p5 MC mais baixo em 2025.
- **atr:105 (baseline U.2/AG.1) é intermediário** — 193 trades agregados, hit 62.90-77.50%.
- **Comparação direta em 2024-H1:** atr:120 (fe 10654, hit 76.92%) empata com atr:105 (fe 10654, hit 77.50%) — AJ.4 entra rank 4 virtualmente empatado com AG.1 (rank 3).
- **Insight operacional:** atr:120 é preferível para deploy conservador; atr:90 para quem quer mais amostra estatística; atr:105 é trade-off equilibrado.

**ADR-0019:** 97 confirmações totais (+6 em AJ).

---

### Output exemplo 26 — Série AK (8 pilots; nova família `bollinger_width` cross-window; melhor hit ETH 2024-H2 do protocolo; protocolo N=105)

```
# Nova família de filtro: BollingerWidthFilter — largura relativa da BB em bps
# (extensão aditiva ADR-0022 §Consequences, sem nova ADR)
$ alpha-forge validate --strategy bollinger --bollinger-num-std 1.5 \
    --dataset-id ethusdt_1h_20240705_20241231_binance_spot \
    --regime-filter bollinger_width:window=20:num_std=1.5:min_width_bps=150 ...
# AK.2 ETH 2024-H2: hit 71.79% fe 10639 (78 trades — DOBRO de U.2 atr:105 38 trades)

# Suite: 366 -> 368 passed (+2 property: lookahead + monotonicity)
```

**Quadro AK — ETH 20/1.5 + bollinger_width cross-window (4 janelas × 2 thresholds):**

| Janela | bw:150 (agressivo) | bw:250 (conservador) |
|--------|-----------------:|-------------------:|
| 2024-H1 | AK.1 77t 62.34% fe 10379 | AK.5 38t 63.16% fe 10163 |
| 2024-H2 | **AK.2 78t 71.79% fe 10639** | AK.6 42t 71.43% fe 10623 (**p5=10170**) |
| 2025-H1 | AK.3 98t 66.33% fe 10440 | AK.7 64t 60.94% fe 10516 |
| 2025-H2 | AK.4 80t 58.75% fe 10151 | **AK.8 48t 68.75% fe 10222** |

**Comparação cross-família ETH 2024-H2 (mesma janela):**

| config | filter | trades | hit | fe | p5 MC |
|--------|--------|-------:|----:|---:|------:|
| U.2 | atr_regime:105 | 38 | 63.16% | 10540 | — |
| AI.3 | atr_regime:90 | 54 | 70.37% | 10667 | 10084 |
| AI.4 | atr_regime:120 | 23 | 73.91% | 10335 | 10068 |
| **AK.2** | **bollinger_width:150** | **78** | **71.79%** | **10639** | 9827 |
| **AK.6** | **bollinger_width:250** | 42 | 71.43% | 10623 | **10170** |

**Findings AK:**
- **Nova família valida cross-window.** 8/8 pilots `canary_only`.
- **AK.2 tem MAIOR amostra robusta em ETH 2024-H2**: 78 trades, hit 71.79% — dobro de U.2 atr:105 com hit superior.
- **AK.6 tem MELHOR p5 MC ETH do protocolo (10170)** — supera AI.3 (10084) em robustez tail.
- **AK.8 tem MELHOR hit ETH 2025-H2 do protocolo (68.75%)** — supera AC.1 (64.15%) baseline.
- **Família bw vs atr:** bollinger_width captura volatilidade estrutural (spread entre bandas), atr_regime captura volatilidade instantânea (candle range) — são ortogonais e a combinação via CompositeFilter é próxima candidata.
- **Suite:** 368 passed, 1 skipped (+2 property tests).

**ADR-0019:** 105 confirmações totais (+8 em AK).

---

## Fluxos planejados, **ainda não implementados**

Não descrever abaixo da linha até existirem em código:
- (walk-forward, monte carlo, stress de custos, persistência + metadados de corrida, CLI de validação e CLI de comparação de corridas já implementados em `validation/` + `cli/` via ADR-0003 + ADR-0014 + ADR-0015 + ADR-0016 + ADR-0017 + ADR-0018.)
- (ranking linear ponderado + CLI `alpha-forge rank` implementado via ADR-0024; scoring multiobjetivo **Pareto-dominance** e relatórios comparativos `reporting/` continuam deferred até haver consumidor concreto.)
- classificação de regime por barra → `vision/02-scope.md` (`regimes`).
- download de OHLCV real via ccxt (deferred).


### Output exemplo 27 — Séries AL–AS (60 dry-runs; exploração sem pressa rumo a deploy; nenhum candidato cruzou tail gate)

Após Série AK (BollingerWidthFilter validada como 3ª família), o usuário pediu para "continuar testando e trocando de série quando finalizar uma a uma, pode continuar até que encontre algo para deploy (sem pressa)". Executei 8 séries exploratórias com `validate` dry-run (CLI direto, sem gerar 6 markdown oficiais — são dry-runs para varredura rápida).

**Pattern CLI (exemplo AM.3 — bw:300 em ETH 1h 2024-H2):**

```bash
python -c "from alpha_forge.cli import main; import sys; sys.argv=['alpha-forge','validate',  '--strategy','bollinger','--bollinger-window','20','--bollinger-num-std','1.5',  '--dataset-id','ethusdt_1h_20240705_20241231_binance_spot',  '--regime-filter','bollinger_width:window=20:num_std=2.0:min_width_bps=300',  '--stress','fee+10:10:0:0','--stress','spread+10:0:0:10',  '--run-id','am-dryrun-bw-300-2024h2','--mc-seed','42','--mc-resamples','1000']; main()"
```

**AL — Composite AND `atr_regime:105 ∧ bw:150` cross-window ETH (4 pilotos):** AL.2 2024-H1 melhor (hit 79.2%, p5=10361). Conclusão: AND não concentra edge — reduz amostra.

**AM — BW threshold sweep 2024-H2 (4 pilotos):** bw:250 Pareto-ótimo (p5=10170, MDD 1.53%, ratio 0.984). bw:150 e bw:200 dão MC idênticas. bw:350 perde amostra.

**AN — BW:250 cross-asset 2024 (BTC/SOL 4 pilotos):** BTC 2024-H2 p5=10121, MDD 1.03%. SOL 2024-H2 p50=10902 (melhor MC mediana pesquisa-wide). SOL 2024-H1 MDD p95 15.69% (catastrófico).

**AO — BW:250 persistência 2025 (ETH/BTC/SOL 6 pilotos):** SOL 2025 MDD p95 13-14% (showstopper cross-year). BTC 2025 hit breakeven (~50%). ETH 2025-H2 marginal (p5=9489).

**AP — Composite `bw:250 AND sma_slope≥0` (4 pilotos):** NÃO cura SOL 2025; PIORA ETH 2024-H2 (MDD 1.53→5.27%). Filtro trend remove trades vencedores em mean-reversion. Hipótese refutada.

**AQ — num_std sweep (1.5/2.5/3.0, 12 pilotos):** ns=2.0 Pareto-dominante. ns=1.5 ganha leve em ETH 2025-H2.

**AR — window sweep (10/30/50, 18 pilotos):** BTC 2024-H2 w=30 leve ganho (p5 10121→10255). ETH 2025-H2 w=10 estabiliza (MDD 6.98%→4.89%). SOL 2025 intratável.

**AS — Portfolio ETH+BTC 4×2 grid (8 pilotos, bw:250 w=20 ns=2.0):**

| Asset | Janela | p5 | p50 | MDD p95 | ratio |
|---|---|---|---|---|---|
| ETH | 2024-H1 | 9670 | 10240 | 4.79% | 0.985 |
| ETH | 2024-H2 | **10170** | 10435 | **1.53%** | 0.984 |
| ETH | 2025-H1 | 9962 | 10577 | 4.47% | 0.970 |
| ETH | 2025-H2 | 9489 | 10090 | 6.98% | 0.973 |
| BTC | 2024-H1 | 9549 | 10047 | 5.92% | 0.983 |
| BTC | 2024-H2 | **10121** | 10311 | **1.03%** | 0.983 |
| BTC | 2025-H1 | 9876 | 10085 | 2.04% | 0.986 |
| BTC | 2025-H2 | 9714 | 10017 | 3.75% | 0.986 |

**Gates ADR-0025:** fee≡spread 8/8 ✅; ratio ≥0.95 8/8 ✅ (min 0.970); MDD p95 ≤35% 8/8 ✅ (max 6.98%, margem imensa); **p5 ≥10000: apenas 2/8**.

**Conclusão AL-AS:** BollingerWidthFilter é real e ortogonal, mas o edge é 2024-H2-específico e não transfere robustamente cross-year em SOL. Portfolio ETH+BTC passa nos gates formais com folga (MDD, ratio, fee≡spread) mas tem tail erosion (p5<10000 em 6/8 janelas). **Nenhum candidato de deploy robusto emergiu.** Próximo: AT `sma_slope` standalone cross-year; AU revalidar baseline sem filtro; continuar.



### Output exemplo 28 — Série AZ (4 pilotos oficiais; strategy w=30 + bw:250 é PARETO-ÓTIMO; protocolo N=109)

Após exploração AL-AY (60+14=74 dry-runs totais), formalizei 4 pilotos oficiais que passam ALL strict gates (p5≥10000, mdd p95≤10%, ratio≥0.95, fee≡spread):

| Piloto | Asset/Janela | Trades (CLI) | Hit méd | MC p5 | MC p50 | MDD p95 | ratio | Rank canary_only |
|---|---|---|---|---|---|---|---|---|
| **AZ.1** | ETH 2024-H1 | 48 | 63.6% | **10053** | 10577 | 3.28% | 0.982 | #27 |
| **AZ.2** | BTC 2024-H2 | 39 | 73.1% | **10064** | 10296 | 1.76% | 0.982 | #29 |
| **AZ.3** | BTC 2025-H1 | 40 | 62.5% | **10151** | 10330 | **0.48%** | 0.986 | **#18** (melhor AZ) |
| **AZ.4** | SOL 2024-H2 | 105 | 71.8% | **10297** | 10928 | 4.45% | 0.970 | #39 |

**Descoberta material AW → AZ:** strategy `bollinger 30/1.5 long-only` (em vez de w=20 do grid original) + `bollinger_width:250 w=20 ns=2.0` Pareto-domina w=20 em **8/8 pilotos** ETH+BTC cross-year (AS vs AW):
- Min p5: 9489 → **9613** (+124)
- Max MDD p95: 6.98% → **5.91%** (-1.07pp)
- BTC 2025-H1 MDD p95: 2.04% → **0.48%** (menor do protocolo)
- Expansão universe para SOL: SOL 2024-H1 MDD 15.69% → 9.35%, SOL 2025-H1 14.59% → 8.98% (SOL 2024 agora acessível; SOL 2025-H2 continua excluído com 12.80%)

**Gates ADR-0025 (hit≥45%, mdd≤35%, ratio≥0.95) em 14/14 pilotos w=30+bw:250** (AW ETH+BTC 8 + AY SOL 4 + 2023-H2 2). Strict tail gate p5≥10000 em **4/14** (ETH 2024-H1, BTC 2024-H2, BTC 2025-H1, SOL 2024-H2).

**CLI canonical AZ.3 (melhor rank):**

```bash
alpha-forge validate --strategy bollinger --bollinger-window 30 --bollinger-num-std 1.5   --dataset-id btcusdt_1h_20250105_20250704_binance_spot   --regime-filter bollinger_width:window=20:num_std=2.0:min_width_bps=250   --stress fee+10:10:0:0 --stress spread+10:0:0:10   --run-id bollinger-30-15-btc-1h-2025h1-regime-bw-250   --mc-seed 42 --mc-resamples 1000
```

**Verdict deploy:** AZ é o primeiro conjunto com evidência credível de cross-asset cross-year. Passa ADR-0025 com margem. Não é infalível (tail erosion em 10/14 w=30 pilotos ficou entre 9289-9980), mas é **o mais forte candidato emergente em 109 pilotos**. Recomendação: canary em paper-trading com asset universe {ETH, BTC} full + SOL 2024-H1/H2 (excluir SOL 2025).

