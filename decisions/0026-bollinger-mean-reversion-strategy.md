# 0026 — Quinta família: Bollinger mean-reversion (long-only)

**Status:** Accepted
**Date:** 2026-04-18
**Deciders:** Usuário (owner do projeto) + agente.

## Context

A Série H encerrou com **12 pilotos trend-following** (Donchian + MA crossover, com e sem filtro de regime, sobre BTC/ETH/SOL 1h 180d) todos em plateau empírico `hit_rate ∈ [24.49%, 32.29%]`. Nenhum cruzou 45% absoluto. ADR-0025 formalizou que o plateau é estrutural para esta família sobre este dataset; ranking ADR-0024 operou primeiro uso e promoveu 3 pilotos a `paper_only` via top-3 relativo.

Os 12 pilotos exerciram 3 assets × 3 janelas (10/5, 20/10, 40/20) × 4 famílias de filtro (none, SMA slope, ATR, AND, OR) + reversal symmetric + 2 families (Donchian + MA). **A dimensão ainda não testada é "família qualitativamente diferente"** — especificamente, **mean-reversion** (entra contra o movimento recente, sai quando reverte) em vez de trend-following (entra com o movimento, sai quando reverte). Hipótese implícita: em timeframe 1h crypto, onde há frequente ruído + ranging (especialmente SOL — H.10 teve mdd=14.55%, maior do protocolo), mean-reversion pode capturar edge que trend-following não captura.

Bollinger Bands é a especificação mais enxuta de mean-reversion com tradição quantitativa: média móvel ± k × desvio-padrão forma um envelope; entrada long quando preço fura a banda inferior (oversold condicional ao próprio histórico recente); saída quando reverte à média. Três parâmetros (`window`, `num_std`, `long_only`); regra puramente observável sobre `close`; zero dependências externas novas.

## Decision

Adicionar `BollingerMeanReversionStrategy(window: int, num_std: float, long_only: bool = True)` em `src/alpha_forge/strategies/families/bollinger/strategy.py`, **long-only nesta fase**. Stateless, causal por construção (`decide(window) -> Signal` é função pura de `window` e parâmetros; ignora `window.iloc[-1]` por construção mesmo com o engine já garantindo causalidade). Integra à CLI via `--strategy bollinger --bollinger-window N --bollinger-num-std K`.

### Regra exata (parte da decisão, não detalhe de implementação)

Dado `window = prices[:t+1]` e parâmetros `window_size`, `num_std`:

Sejam `closes = window["close"].iloc[:-1]` (todos os closes até `t-1` inclusive — a barra `t` é ignorada por construção, mesmo o engine garantindo).

Sejam `mu_prev = mean(closes.iloc[-window_size-1 : -1])`, `sigma_prev = pstdev(closes.iloc[-window_size-1 : -1])` (a média/desvio sobre as `window_size` barras **anteriores a `t-1`**), e `mu_now`, `sigma_now` análogos sobre `closes.iloc[-window_size:]`.

- **Entrada long em `t`** quando `close[t-1] < mu_now - num_std * sigma_now` **e** `close[t-2] >= mu_prev - num_std * sigma_prev`. Isto é: a barra `t-1` **cruzou para dentro** da região oversold (estritamente abaixo da banda inferior), vindo de fora ou da borda. Cruzamento estrito; já-estar-dentro da região não dispara sinal repetido (stateless).
- **Saída em `t`** quando `close[t-1] >= mu_now` **e** `close[t-2] < mu_prev`. Isto é: a barra `t-1` **cruzou de baixo para cima** a média móvel — exit na volta ao mean. Cruzamento estrito; já-estar-acima não dispara exit repetido.
- **Ordem de avaliação:** primeiro testa saída, depois entrada. No caso raro de ambos dispararem na mesma barra (artifact numérico extremo), EXIT vence — arbitragem conservadora simétrica à ADR-0011.
- **Warm-up:** `HOLD` enquanto `len(window) < window_size + 3`. Precisa-se de `window_size` barras anteriores para `mu_prev`/`sigma_prev`, + 1 barra para `t-2`, + 1 para `t-1`, + 1 para `t` (ignorada).

A regra é declaradamente **cruzamento de banda** (edge-triggered), não "estar na zona" (level-triggered). Stateless + edge-triggered elimina necessidade de memória de posição na estratégia; redundância de sinais fica a cargo do engine (como em ADR-0011 §"Separação").

### Contrato de parâmetros (parte da decisão)

Validação cedo no `__init__`, mesmo rigor de ADR-0008 / ADR-0011:

- `window` deve ser `int` verdadeiro (rejeita `bool`, rejeita `float`-que-é-inteiro). `> 0`. Violação → `TypeError` ou `ValueError`.
- `num_std` deve ser `float` ou `int` (`bool` rejeitado). `> 0`. Violação → `TypeError` ou `ValueError`. `num_std = 0` rejeitado (banda degenera em linha).
- `long_only` deve ser `bool` verdadeiro. Só `True` é suportado nesta ADR; `False` → `NotImplementedError` com mensagem clara ("mean-reversion short side: ADR futura"). Explicit better than implicit.
- Sem defaults no construtor. Defaults vivem na CLI (`window=20, num_std=2.0`, valores canônicos de Bollinger clássico).
- Parâmetros congelados no `__init__`; validação nunca dentro de `decide()`.

### Separação estratégia × engine (parte da decisão)

- `decide(window) -> Signal` retorna apenas `ENTER_LONG`, `EXIT`, `HOLD`. `ENTER_SHORT` nunca emitido (long-only rígido).
- Stateless absoluto. Nenhum `self._last_signal`, `self._in_position`, etc.
- Sinais redundantes possíveis (e.g., `ENTER_LONG` seguido de outro `ENTER_LONG` antes de um EXIT real): engine reduz a no-op como já faz hoje ([engine.py:171-172](../src/alpha_forge/backtest/engine.py#L171-L172)).

### Integração com CLI (parte da decisão)

- `--strategy` ganha `bollinger`: `--strategy {ma_crossover,dummy,donchian,bollinger}`. `ma_crossover` continua default.
- Duas flags dedicadas: `--bollinger-window` (default 20) e `--bollinger-num-std` (default 2.0).
- `--long-only/--symmetric` atua sobre `bollinger` mas `--symmetric` levanta `NotImplementedError` no construtor — documentado no `--help`.
- Summary imprime `strategy: bollinger window=20 num_std=2.0`.

### Caracterização inicial e piloto I.1

Primeira execução do Bollinger será **piloto agentic I.1** (`bollinger-20-2-sol-180d-baseline`) — SOL 1h 180d, `window=20, num_std=2.0, long_only=True`, 6 artefatos agentic + 4 JSONs de validação + `release_decision` sob critério híbrido (ADR-0025). Caracterização é **observação empírica sobre dataset existente**, não tuning nem validação de edge.

### Property-based de monotonicidade de custo (follow-up explícito)

Replicar matriz ADR-0010 para Bollinger: `test_cost_monotonicity_bollinger.py` com property-based verificando que `fe(perturbed) <= fe(baseline)` para `fee_delta_bps >= 0`, `slippage_delta_bps >= 0`, `spread_delta_bps >= 0` (ADR-0019 eixo incluído). Long-only only nesta entrega (mean-reversion short fica para ADR futura).

## Consequences

- **Positive:** quinta família de estratégia no núcleo, cobrindo regime qualitativamente diferente (mean-reversion vs. trend-following); reutiliza integralmente o contrato do engine; valida ADR-0002 (janela causal) sobre uma 3ª forma de sinal; primeiro consumidor pós-Série H sob critério híbrido ADR-0025; habilita ranking cross-family genuíno (antes só trend-following disputava entre si).
- **Negative:** superfície de flags CLI cresce (6 flags de estratégia agora: 2 MA, 2 Donchian, 2 Bollinger) — chegando no limite "revisar quando ≥ 5 estratégias" de ADR-0011. Próxima família exigirá refatoração de flags (e.g., `--strategy-params k=v,k=v`) ou acomodação. Long-only rígido nesta ADR significa que revisitar mean-reversion short exige nova ADR.
- **Neutral:** ADR-0023 (CompositeFilter) e ADR-0022 (Regime filter) continuam aplicáveis — Bollinger pode ser combinado com `--regime-filter` como qualquer outra estratégia. Não cria dívida arquitetural.

### Fica explicitamente fora desta ADR

1. **Short side** (`long_only=False`). Mean-reversion short tem asimetria estrutural (não há teto natural de preço como há piso em 0); requer discussão dedicada. ADR futura.
2. **Stops / targets / trailing**. Única saída é retorno à média. Stops interagem não-trivialmente com mean-reversion (uma thesis de "preço reverte" conflita com "stop quando preço continua contra"); ADR futura se houver motivo.
3. **Bollinger Band Width / %B** ou métricas derivadas como features. Nesta ADR é regra de entrada/saída, não feature engineering.
4. **Calibração de `num_std` no dataset**. `2.0` é valor clássico (Bollinger original), explicitamente não-otimizado sobre SOL/BTC/ETH 180d. Grid search intra-walk-forward proibido por ADR-0003.
5. **`rolling` do pandas**. Implementação usa `iloc` + `.mean()` / `.std(ddof=0)` diretamente para preservar estilo explícito das outras famílias (sem dependência de quirks de `rolling.min_periods` / `rolling.closed`).

### Critério de sucesso

ADR-0026 está **concluída** quando:

- `BollingerMeanReversionStrategy` existe em `src/alpha_forge/strategies/families/bollinger/strategy.py`, valida parâmetros cedo, é stateless, ignora `window.iloc[-1]` por construção, edge-triggered em ambos lados (entrada + saída).
- Bateria unit em `tests/unit/test_bollinger_mean_reversion.py` passa em verde (classes nomeadas: `TestValidacaoParametros`, `TestWarmUp`, `TestEntradaCruzandoBandaInferior`, `TestSaidaCruzandoMedia`, `TestArbitragemEntradaSaidaSimultaneas`, `TestIgnoraBarraCorrente`, `TestLongOnly`, `TestStateless`).
- Property-based em `tests/property/test_bollinger_causal.py` passa em verde sem flakiness (`window=5, num_std=2.0`, gerador respeitando invariantes mínimos de OHLC).
- Property-based em `tests/property/test_cost_monotonicity_bollinger.py` passa em verde (eixos fee/slippage/spread). Matriz total: 5 famílias × modos, Bollinger long-only é a 7ª entrada.
- CLI integrada: `--strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0` roda em `run-demo` e `validate`.
- Piloto agentic I.1 (6 artefatos + 4 JSONs) encerrado com `release_decision` sob ADR-0025.
- `system/api.md`, `system/flows.md`, `STATE.md` atualizados.

Explicitamente fora do critério:

- Qualquer alvo numérico (`hit_rate`, `final_equity`, etc.).
- Comparação numérica com Donchian ou MA crossover além da ordenação via ranking.
- Promoção automática a `paper_only` — critério híbrido ADR-0025 decide caso a caso.

## Alternatives considered

- **RSI mean-reversion em vez de Bollinger** — rejeitado: RSI tem smoothing não-trivial (Wilder EMA vs SMA), introduz parametrização opaca (`overbought=70`, `oversold=30` são convenções frágeis). Bollinger é `mean ± k*std`, transparente; zero ambiguidade de implementação.
- **Edge-triggered baseado em `low[t-1]` / `high[t-1]`** em vez de `close[t-1]` — rejeitado: Bollinger clássico opera em close; usar low/high sobrepõe com Donchian (mesma superfície de alta/baixa). Mantém famílias discriminadas na dimensão de observação.
- **Saída quando atinge banda superior** (`mu + k*sigma`) em vez de média — rejeitado: saída em banda superior assume edge de "overshoot após reversão", hipótese forte. Saída em média é definição mínima de "reverteu"; usa-se o fato de entrar abaixo e sair quando volta.
- **Level-triggered** (entra enquanto `close < mu - k*sigma`, sai enquanto `close >= mu`) — rejeitado: força stateful ou engine-dependency para não emitir sinais repetidos; edge-triggered é estilisticamente consistente com Donchian / MA crossover.
- **Incluir short side nesta ADR** (`long_only=False` emitindo ENTER_SHORT acima da banda superior) — rejeitado: mean-reversion short tem asymmetries estruturais (ver §"Fica fora"); merece ADR própria.
- **`std` com `ddof=1` (sample stdev)** em vez de `ddof=0` (population stdev) — rejeitado: `pstdev` (ddof=0) é consistente com ADR-0024 (`fold_std_hit`) e com a interpretação "desvio do window observado", não "estimador de desvio populacional subjacente". Pequena magnitude, mas consistência importa.
- **Janela única `window` usada também para outras métricas (e.g., `num_std` de uma janela maior)** — rejeitado: adiciona superfície de hiperparâmetros sem ganho de interpretabilidade.
- **Parâmetros `window=20, num_std=2.0` hardcoded** (sem flag CLI) — rejeitado: imóvel, impede pilotos de sensibilidade; mesmo padrão das outras famílias com flags dedicadas.
- **`bool` default `long_only=False`** (short-first) — rejeitado: as 4 famílias existentes têm `long_only=True` default; quebrar padrão sem motivo.
- **Deixar `num_std = 0` válido** (banda degenera em linha = mean crossover) — rejeitado: duplica MA crossover degenerado; melhor falhar cedo com ValueError.

## Follow-ups

Concrete actions this decision creates. Each one belongs in `STATE.md` as pending work.

- Implementar `src/alpha_forge/strategies/families/bollinger/__init__.py` + `strategy.py` conforme §"Regra exata" + §"Contrato de parâmetros".
- Implementar `tests/unit/test_bollinger_mean_reversion.py` com classes nomeadas conforme §"Critério de sucesso".
- Implementar `tests/property/test_bollinger_causal.py` (`window=5, num_std=2.0`; gerador de OHLC respeitando invariantes).
- Implementar `tests/property/test_cost_monotonicity_bollinger.py` — matriz fee/slippage/spread, long-only.
- Atualizar `src/alpha_forge/cli/app.py`: `bollinger` no enum; `--bollinger-window` / `--bollinger-num-std`; `_build_strategy` e `_strategy_param_label`.
- Rodar suíte completa, confirmar verde sem flakiness.
- Abrir piloto I.1 `bollinger-20-2-sol-180d-baseline`: 6 artefatos agentic + `alpha-forge validate` + 4 JSONs + `release_decision` sob ADR-0025 + snapshot de ranking pós-inclusão (13 pilotos, top-3 redefinido).
- Atualizar `system/api.md` (módulo + flags + `--help`), `system/flows.md` (output de caracterização + fluxo validação), `src/alpha_forge/strategies/README.md`, `STATE.md`.
- **Explicitamente fora:** mean-reversion short side, stops/targets, calibração de `num_std`, composição com Bollinger em `CompositeFilter`.
