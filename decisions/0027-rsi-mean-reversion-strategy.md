# 0027 — Sexta família: RSI mean-reversion (long-only, SMA-smoothed)

**Status:** Accepted
**Date:** 2026-04-18
**Deciders:** Usuário (owner do projeto) + agente.

## Context

Séries I + J + K (10 pilotos Bollinger 20/2 em 1h, cross-asset + cross-window + hyperparameters) confirmaram edge mean-reversion como `canary_only` consistente. Séries L (15m) + M (4h) delimitaram formalmente o sweet spot em 1h (3/3 `fail` em cada direção).

A pergunta aberta é: **edge mean-reversion em 1h é propriedade da família Bollinger ou de mean-reversion em geral?** Sem uma segunda família, não há como discriminar. Se uma segunda família mean-reversion replicar o sinal, a conclusão é estrutural ("mean-reversion captura algo real neste timeframe"); se não replicar, o edge é específico da regra Bollinger (envelope média ± k·σ).

ADR-0026 §"Alternatives considered" rejeitou RSI explicitamente pelo argumento "smoothing não-trivial (Wilder EMA vs SMA), introduz parametrização opaca". Esse argumento é válido contra RSI *como Wilder o definiu*, mas é uma escolha de implementação — **pode-se adotar RSI com smoothing SMA simples**, preservando transparência do estilo Bollinger. Isso resolve a objeção de ADR-0026 sem descartar a família.

A motivação de adicionar RSI agora (e não antes) é discriminativa, não especulativa: o protocolo precisa de uma segunda família mean-reversion para testar generalização; Bollinger e RSI são as duas canônicas da literatura. Ambas são "condicional ao histórico recente", mas observam coisas diferentes: Bollinger vê **amplitude** de desvio (preço ± σ), RSI vê **velocidade/momentum** (razão ganhos/perdas).

## Decision

Adicionar `RSIMeanReversionStrategy(period: int, oversold: float, overbought: float, long_only: bool = True)` em `src/alpha_forge/strategies/families/rsi/strategy.py`, **long-only nesta fase**. Stateless, causal por construção (ignora `window.iloc[-1]`). **Smoothing SMA simples** (não Wilder EMA). Integra à CLI via `--strategy rsi --rsi-period N --rsi-oversold K --rsi-overbought M`.

### Regra exata (parte da decisão)

Dado `window = prices[:t+1]` e parâmetros `period`, `oversold`, `overbought`:

Seja `closes = window["close"].iloc[:-1]` (barra `t` ignorada por construção).

Sejam `deltas = closes.diff().iloc[1:]` (primeira diferença, N-1 valores para N closes). Sejam:

- `gains_t = max(deltas, 0)` (ganhos; perdas viram 0).
- `losses_t = -min(deltas, 0)` (perdas positivas; ganhos viram 0).

**RSI em `t-1`** (último índice disponível em `closes`):

- `avg_gain_now = mean(gains.iloc[-period:])`
- `avg_loss_now = mean(losses.iloc[-period:])`
- Se `avg_loss_now == 0`: `rsi_now = 100.0` (caso degenerado: só ganhos no período).
- Senão: `rs_now = avg_gain_now / avg_loss_now`; `rsi_now = 100 - 100 / (1 + rs_now)`.

**RSI em `t-2`** (um índice atrás, para edge-triggered):

- `avg_gain_prev = mean(gains.iloc[-period-1:-1])`
- `avg_loss_prev = mean(losses.iloc[-period-1:-1])`
- `rsi_prev` análogo a `rsi_now`.

Sinais edge-triggered (cruzamento estrito):

- **Entrada long em `t`** quando `rsi_now < oversold` **e** `rsi_prev >= oversold`. Isto é: a barra `t-1` cruzou para dentro da região oversold.
- **Saída em `t`** quando `rsi_now >= 50.0` **e** `rsi_prev < 50.0`. Isto é: RSI cruzou de baixo para cima a linha neutra 50 — saída na volta ao equilíbrio de momentum.
- **Ordem:** EXIT antes de ENTER_LONG (arbitragem conservadora, consistente com ADR-0011 / ADR-0026).
- **Warm-up:** `HOLD` enquanto `len(window) < period + 3`. Precisa `period` deltas para `avg_*_now` + 1 delta para `avg_*_prev` + 1 close para `t-1` + 1 close para `t` (ignorada).

A regra é declaradamente **cruzamento de nível** (edge-triggered em oversold e em 50), não "estar na zona". Stateless + edge-triggered, mesmo padrão de ADR-0026.

### Por que saída em RSI=50, não em `overbought=70`?

Saída em `overbought` assume edge de "overshoot após reversão" (captura o movimento inteiro de oversold→overbought). Saída em 50 é a definição mínima de "reverteu" — usa-se o fato de entrar em oversold e sair quando momentum volta ao equilíbrio. Padrão é simétrico a ADR-0026 §"Saída quando atinge banda superior" (também rejeitado lá pela mesma razão). `overbought` entra na superfície de parâmetros apenas para *reservar* o simétrico short side em ADR futura; no long-only atual, `overbought` é **não-usado** mas validado para manter o shape de config estável entre ADRs (evita breaking change quando short for adicionado).

### Por que SMA, não Wilder EMA?

ADR-0026 §"Alternatives considered" rejeitou RSI por "smoothing não-trivial (Wilder EMA vs SMA)". Usar SMA resolve a objeção:

- Wilder EMA tem coeficiente `1/period` implícito, mistura histórico antigo sem bound explícito, exige seed (valor inicial das primeiras `period` barras é calculado diferente das subsequentes) → introduz parametrização opaca.
- SMA é `.iloc[-period:].mean()` — idêntico a Bollinger. Transparente, reprodutível, sem seed.
- Consequência empírica: RSI-SMA reage mais rápido a mudanças recentes que RSI-Wilder (não há ponderação exponencial). Para timeframe 1h com janela ~14 barras, a diferença é mensurável mas não qualitativamente distinta; para protocolo deste projeto (foco em discriminar famílias, não em replicar comportamento canônico de TradingView/MT5), SMA é escolha correta.
- **Trade-off honesto:** RSI-SMA não é o "RSI clássico" da literatura Wilder 1978; é uma variante consciente. Nome da classe reflete isso implicitamente (não há `RSIWilder` vs `RSI_SMA` separados) — se no futuro quisermos Wilder, será ADR nova.

### Contrato de parâmetros (parte da decisão)

- `period` deve ser `int` verdadeiro (rejeita `bool`, rejeita `float`). `> 0`. Violação → `TypeError` ou `ValueError`.
- `oversold` deve ser `float` ou `int` (`bool` rejeitado). `0 < oversold < 50`. `>= 50` rejeitado (viola semântica de "oversold").
- `overbought` deve ser `float` ou `int` (`bool` rejeitado). `50 < overbought < 100`. `<= 50` rejeitado.
- `long_only` deve ser `bool`. Só `True` suportado; `False` → `NotImplementedError`.
- Sem defaults no construtor. Defaults vivem na CLI (`period=14, oversold=30, overbought=70`, canônicos de Wilder).
- Parâmetros congelados no `__init__`; validação nunca dentro de `decide()`.

### Separação estratégia × engine (parte da decisão)

- `decide(window) -> Signal` retorna apenas `ENTER_LONG`, `EXIT`, `HOLD`. `ENTER_SHORT` nunca emitido (long-only rígido).
- Stateless absoluto.
- Sinais redundantes → engine absorve (mesmo padrão).

### Integração com CLI (parte da decisão)

- `--strategy` ganha `rsi`: `--strategy {ma_crossover,dummy,donchian,bollinger,rsi}`.
- Três flags dedicadas: `--rsi-period` (default 14), `--rsi-oversold` (default 30.0), `--rsi-overbought` (default 70.0).
- `--long-only/--symmetric` atua; `--symmetric` → `NotImplementedError`.
- Summary imprime `strategy: rsi period=14 oversold=30.00 overbought=70.00`.

**Nota sobre a superfície de flags CLI:** ADR-0026 §Consequences previu que a próxima família (6ª) exigiria refatoração de flags (`--strategy-params k=v,k=v`). Decidimos **adiar a refatoração** — RSI adiciona 3 flags nomeadas (segue o padrão), não 1 dict opaco. Refatoração fica para a 7ª família, se houver. Custo aceito: 9 flags de estratégia no `--help` (2 MA + 2 Donchian + 2 Bollinger + 3 RSI). Benefício preservado: cada família tem flags explícitas, documentadas, descobríveis via `--help`.

### Caracterização inicial e pilotos Série N

Primeira execução do RSI será **Série N cross-asset**: N.1 SOL + N.2 BTC + N.3 ETH, 1h 2024-H2 (mesma janela de Série J para comparação direta), `period=14, oversold=30, overbought=70, long_only=True`. 3 × 6 artefatos agentic + 3 × 4 JSONs + `release_decision` sob ADR-0025 + ranking pós-inclusão.

### Property-based de causalidade e monotonicidade (follow-up explícito)

- `tests/property/test_rsi_causal.py` — Hypothesis gera OHLC, valida que mutação em `window.iloc[-1]` ou em barras futuras não altera sinal. Padrão ADR-0026.
- `tests/property/test_cost_monotonicity_rsi.py` — Matriz fee/slippage/spread. Aplicação mecânica de ADR-0010 + ADR-0019 à 6ª família. Long-only only.

## Consequences

- **Positive:** sexta família de estratégia; primeira segunda-família mean-reversion; habilita discriminação "edge é da família ou do regime"; reusa integralmente contrato do engine; valida ADR-0002 sobre uma 4ª forma de sinal; ranking cross-family agora entre duas famílias mean-reversion + três trend-following.
- **Negative:** CLI ganha 3 flags (total 9 específicas de estratégia); refatoração de flags adiada para a 7ª família; RSI-SMA não é o RSI clássico Wilder (diferença consciente documentada).
- **Neutral:** ADR-0022 (regime filter) e ADR-0023 (CompositeFilter) aplicam-se a RSI como a qualquer estratégia; long-only rígido mantém padrão das outras famílias.

### Fica explicitamente fora desta ADR

1. **Short side** (`long_only=False`) — ENTER_SHORT quando `rsi_now > overbought ∧ rsi_prev <= overbought`; EXIT quando `rsi_now <= 50 ∧ rsi_prev > 50`. ADR futura.
2. **Wilder EMA smoothing** — ADR separada se houver demanda.
3. **Stops / targets / trailing.**
4. **Divergência preço-RSI** (higher-highs em preço vs lower-highs em RSI) como feature — não é regra de entrada nesta ADR.
5. **Calibração de `period/oversold/overbought`** no dataset — valores canônicos 14/30/70 não-otimizados; grid search proibido por ADR-0003.

### Critério de sucesso

ADR-0027 está **concluída** quando:

- `RSIMeanReversionStrategy` existe, valida parâmetros cedo, é stateless, ignora `window.iloc[-1]`, edge-triggered em entrada e saída.
- Bateria unit em `tests/unit/test_rsi_mean_reversion.py` (classes: `TestValidacaoParametros`, `TestWarmUp`, `TestEntradaCruzandoOversold`, `TestSaidaCruzandoMeio`, `TestArbitragemEntradaSaidaSimultaneas`, `TestIgnoraBarraCorrente`, `TestLongOnly`, `TestStateless`).
- Property-based em `tests/property/test_rsi_causal.py` passa sem flakiness.
- Property-based em `tests/property/test_cost_monotonicity_rsi.py` passa.
- CLI integrada: `--strategy rsi --rsi-period 14 --rsi-oversold 30 --rsi-overbought 70` roda em `run-demo` e `validate`.
- Série N (N.1/N.2/N.3, 6+6+6 artefatos + 12 JSONs) encerrada com `release_decision` sob ADR-0025.
- `system/api.md`, `system/flows.md`, `STATE.md` atualizados.

Explicitamente fora do critério:

- Qualquer alvo numérico.
- Comparação direta Bollinger vs RSI além de ranking.
- Promoção automática a `paper_only`.

## Alternatives considered

- **RSI com smoothing Wilder EMA** — rejeitado: introduz seed/valor inicial diferente das barras subsequentes; menos reprodutível que SMA. Reconsiderar em ADR futura se houver motivo empírico.
- **Saída em `overbought` em vez de 50** — rejeitado: hipótese forte de overshoot; simétrico a ADR-0026.
- **Level-triggered** (sem checar cruzamento de `t-2 → t-1`) — rejeitado: força stateful ou engine-dependency; inconsistente com ADR-0026.
- **`overbought` não na API** (só `oversold` no long-only) — rejeitado: exigiria breaking change quando short for adicionado (ADR-0027 valida `overbought`, ADR futura usa); manter shape estável agora.
- **`oversold=30, overbought=70` hardcoded** — rejeitado: impede pilotos de sensibilidade; mesmo padrão de Bollinger.
- **`period=14` como único parâmetro** (oversold/overbought = constantes 30/70) — rejeitado: reduz expressividade; Série futura pode explorar 20/80 ou 25/75 (mesma estrutura de K vs J em Bollinger).
- **Combinar RSI com Bollinger em single strategy ("oversold AND below lower band")** — rejeitado: viola "uma ideia por ADR"; composição fica para ADR de meta-estratégia (futura).
- **Pular ADR e implementar direto** — rejeitado: RSI foi explicitamente rejeitado em ADR-0026 §Alternatives; reverter essa rejeição exige ADR explícita.

## Follow-ups

- Implementar `src/alpha_forge/strategies/families/rsi/__init__.py` + `strategy.py`.
- Implementar `tests/unit/test_rsi_mean_reversion.py` com classes nomeadas.
- Implementar `tests/property/test_rsi_causal.py` + `tests/property/test_cost_monotonicity_rsi.py`.
- Atualizar `src/alpha_forge/cli/app.py`: `rsi` no enum; 3 flags; `_build_strategy`; `_strategy_param_label`.
- Rodar suíte completa, verde sem flakiness.
- Abrir Série N: 3 pilotos + rankings.
- Atualizar `system/api.md`, `system/flows.md`, `STATE.md`.
- **Explicitamente fora:** mean-reversion short, Wilder EMA, stops/targets, divergência, calibração de parâmetros.
