# 0011 — Segunda estratégia real: Donchian breakout (long-only)

**Status:** Accepted
**Date:** 2026-04-16
**Deciders:** Usuário (owner do projeto) + agente.

## Context

ADR-0008 entregou a primeira estratégia real (MA crossover causal long-only) e fixou o padrão arquitetural para famílias de estratégia: validação cedo no `__init__`, `decide(window) -> Signal` puro e stateless, separação rígida estratégia×engine, warm-up explícito, tipos inequívocos. ADR-0009 entregou o primeiro dataset real (BTCUSDT 1h, 180 dias, Binance Vision). ADR-0010 fechou o contrato de custo com property-based de monotonicidade. O núcleo está suficientemente maduro para receber uma **segunda** estratégia sem puxar nada segurado (`validation/`, `ranking/`, `regimes/`).

O usuário escolheu **Donchian breakout** explicitamente, preferindo breakout antes de RSI. Donchian é a escolha natural nesta fase: regra cristalina (`high[t-1] > max(high janela anterior)`), long-only defensável, causalidade por construção, sem parâmetros opacos. Cobre um regime de decisão diferente da MA (tendência rompida vs. tendência persistente) e expõe o laboratório a um tipo de sinal com perfil de trade distinto (poucos trades longos vs. muitos trades curtos da MA no sintético).

A MA crossover sobre o sintético foi estruturalmente perdedora (ADR-0008 §8: "objetivo não é ser boa"). O Donchian será caracterizado inicialmente no dataset real BTCUSDT 180d, porque o sintético atual (drift baixo + ruído Gaussiano) é exatamente o pior caso para breakout — sem tendência persistente para romper. Essa escolha de recorte é observacional, não validativa.

## Decision

Adicionar `DonchianBreakoutStrategy(entry_window: int, exit_window: int)` em `src/alpha_forge/strategies/families/donchian/strategy.py`, com defaults `(20, 10)` **apenas na CLI** (construtor exige os dois argumentos). Long-only, stateless, causalidade garantida por construção (regra ignora `window.iloc[-1]` mesmo com o engine já garantindo). Integra à CLI via `--strategy donchian --entry-window N --exit-window M`.

### Regra exata (parte da decisão, não detalhe de implementação)

Dado `window = prices[:t+1]` e parâmetros `entry_window`, `exit_window`:

- **Entrada long em `t`** quando `high[t-1] > max(high[t-entry_window-1 : t-1])`.
- **Saída em `t`** quando `low[t-1] < min(low[t-exit_window-1 : t-1])`.
- **Ordem de avaliação:** primeiro testa a condição de saída, depois a condição de entrada. O engine resolve o efeito operacional com base no estado de posição.
- **Warm-up:** `HOLD` enquanto `len(window) < max(entry_window, exit_window) + 2`.

A janela de comparação **exclui** a barra `t-1` (é o máximo/mínimo das `N` barras anteriores a `t-1`). O rompimento é detectado pela barra imediatamente anterior (`t-1`), e a execução continua em `t+1 open` via engine (ADR-0002, contrato de causalidade inalterado). A estratégia ignora `window.iloc[-1]` (barra `t`) por construção — mesmo que o engine já garanta causalidade no loop, a regra fica inequivocamente causal no nível do código da estratégia. Rompimento é estritamente `>` / `<`, nunca `≥` / `≤` — empate exato não é sinal.

### Contrato de parâmetros (parte da decisão)

Validação cedo no `__init__`, mesmo rigor de ADR-0008:

- `entry_window` e `exit_window` devem ser `int` **verdadeiros**. `bool` é explicitamente rejeitado (`bool` é subclasse de `int` em Python). `float` que "é inteiro" (ex: `20.0`) é rejeitado. Violação → `TypeError`.
- Ambos devem ser `> 0`. Violação → `ValueError`.
- **Sem restrição de ordenação** entre os dois. `entry_window >= exit_window` (ex: Turtle 20/10), `entry_window < exit_window` (ex: 10/20) e `entry_window == exit_window` (ex: 14/14) são todos configurações válidas. Qual é "certa" é hipótese de estratégia, não contrato estrutural.
- **Sem defaults no construtor.** Defaults (20/10) vivem apenas na CLI. Construtor exige ambos argumentos explícitos — garante que nenhum caller programático "esquece" e pega default silenciosamente.
- Parâmetros são validados e congelados no `__init__`. Configuração inválida falha no momento de construção da estratégia, **nunca dentro de `decide()`**.

### Separação estratégia × engine (parte da decisão)

- `decide(window) -> Signal` retorna apenas `ENTER_LONG`, `EXIT` ou `HOLD`. `ENTER_SHORT` **não** faz parte do universo de saída desta estratégia (long-only nesta fase).
- Stateless absoluto. Nenhum `self._last_signal`, `self._in_position`, `self._entry_bar`, cache de cálculo ou memória de execução. O único estado que sobrevive entre chamadas são os dois parâmetros imutáveis.
- A estratégia pode emitir sinais redundantes (ex: `ENTER_LONG` repetido em barras consecutivas enquanto já estou comprado, ou `EXIT` sem posição aberta). **Isso não é erro.** A redução desses sinais a no-op é responsabilidade deliberada do engine, que já trata esses casos hoje em [engine.py:171-172](../src/alpha_forge/backtest/engine.py#L171-L172) e [engine.py:228-229](../src/alpha_forge/backtest/engine.py#L228-L229).
- No caso raro de barra em que `high[t-1]` rompe o máximo **e** `low[t-1]` rompe o mínimo simultaneamente, a ordem EXIT→ENTER_LONG resolve: a estratégia emite `EXIT` primeiro. Com posição aberta, o engine fecha; sem posição, o engine trata como no-op e a própria barra não produz entrada (na barra seguinte, se a condição de entrada persistir, a entrada acontece).

### Integração com CLI (parte da decisão)

- Enum `--strategy` ganha `donchian`: `--strategy {ma_crossover,dummy,donchian}`. `ma_crossover` continua default.
- Duas flags novas dedicadas: `--entry-window` (default 20) e `--exit-window` (default 10). Nomes batem com os parâmetros do construtor.
- Flags específicas de estratégia são ignoradas quando a estratégia ativa não as usa (ex: `--short-window` com `--strategy donchian`). `--help` e `system/api.md` deixam claro qual flag pertence a qual estratégia.
- Summary imprime `strategy: donchian entry=20 exit=10`, mesmo padrão de ADR-0008.
- `run-demo` continua executando **um** backtest por invocação. Comparação lado a lado entre estratégias é trabalho de `ranking/reporting/`, deliberadamente segurado.

### Caracterização inicial (parte da decisão)

A primeira execução real do Donchian será sobre o dataset real `btcusdt_1h_20250705_20251231_binance_spot` (ADR-0009), não sobre o sintético seminal. Motivo operacional: o sintético é drift-baixo + ruído Gaussiano, regime anti-breakout por construção; caracterização sobre ele seria pouco informativa.

Essa caracterização inicial é **observação**, não validação nem prova de edge. O output do `run-demo` entra em `system/flows.md` como achado factual (bars/trades/final_equity/hit_rate/max_drawdown) sem qualquer juízo de valor. Não substitui trabalho futuro de `validation/`.

## Consequences

- **Positive:** segunda família de estratégia no núcleo, cobrindo regime de decisão distinto da MA; reutiliza integralmente o contrato do engine sem puxar nada novo; a própria chegada ao núcleo exercita o suporte a múltiplas estratégias na CLI (`_build_strategy` ganha terceiro ramo natural); dataset real BTCUSDT 180d deixa de estar subutilizado (hoje só o integration test o exercita); padrão unit + property-based replicado idêntico ao de ADR-0008 reforça o estilo de teste do projeto.
- **Negative:** superfície de flags da CLI cresce (quatro flags específicas de estratégia agora: duas da MA, duas do Donchian) — aceitável enquanto houver ≤ 3–4 estratégias, precisa ser revisto quando virar ≥ 5; `--help` fica levemente mais carregado; mais código a manter em `strategies/families/`.
- **Neutral:** sinaliza que o laboratório está pronto para múltiplas estratégias reais; próximas ADRs (short side, RSI, etc.) herdam o padrão; não cria dívida arquitetural.

### Fica explicitamente fora desta ADR

1. **Short side.** Mesma postura de ADR-0008: long-only nesta fase. Short vira ADR própria quando fizer sentido operacional, não como penduricalho.
2. **Stops / targets.** Nenhum stop-loss, trailing stop, profit target, ou filtro de volatilidade. A única saída é o rompimento da baixa. Stops interagem de forma não-trivial com sizing e cost model — empurrar para ADR dedicada quando houver motivo concreto.
3. **Portfolio-level ou avaliação conjunta multi-asset.** Portfolio-level fica fora desta ADR. A estratégia continua compatível com execução por dataset individual, e rodar múltiplos ativos em paralelo permanece responsabilidade do caller/orquestrador.
4. **Filtros de regime.** Nada de "só entrar se ADX > 25" ou "só entrar se volatilidade < X". `regimes/` é `vision/`, não realidade.
5. **Otimização de parâmetros.** Escolher `(entry_window, exit_window)` sobre o dataset é trabalho de `validation/` + `ranking/`, ambos segurados. Os defaults 20/10 vêm da literatura Turtle, explicitamente **não-otimizados** sobre o dataset BTCUSDT 180d.
6. **Monotonicidade de custo property-based para Donchian.** ADR-0010 §5 declarou escopo restrito à estratégia ativa na época. Replicar para Donchian é trabalho mecânico; fica como follow-up **explícito** desta ADR, não pendurado implicitamente.

### Critério de sucesso

ADR-0011 está **concluída** quando:

- `DonchianBreakoutStrategy` existe em `src/alpha_forge/strategies/families/donchian/strategy.py`, valida parâmetros cedo, é stateless, ignora `window.iloc[-1]` por construção, e respeita a ordem EXIT→ENTER_LONG na barra de arbitragem.
- Bateria unit em `tests/unit/test_donchian_breakout.py` passa em verde (classes nomeadas no padrão ADR-0008, sem parametrização opaca).
- Property-based em `tests/property/test_donchian_causal.py` passa em verde sem flakiness (entry_window=5, exit_window=3, hypothesis respeitando invariantes mínimos de OHLC no gerador).
- `--strategy donchian --entry-window 20 --exit-window 10` roda no `run-demo` sobre o dataset real BTCUSDT 180d sem quebrar, e o output é capturado em `system/flows.md`.
- `system/domain.md`, `system/api.md`, `system/flows.md` e `STATE.md` refletem a nova estratégia.

A ADR-0011 está concluída quando o comportamento observado é consistente com o contrato definido, **independentemente** de o resultado econômico no dataset real ser bom, ruim ou neutro. Caracterização é observação, não promoção.

Explicitamente fora do critério de sucesso:

- Qualquer alvo numérico de `total_pnl`, `hit_rate`, `max_drawdown` ou `final_equity`.
- Qualquer comparação numérica entre Donchian e MA crossover.

## Alternatives considered

- **Usar `close[t-1]` em vez de `high[t-1]`/`low[t-1]` como base do breakout** — rejeitado: Donchian clássico é sobre high/low por definição; usar close simplifica a regra sem razão estrutural e descaracteriza a família.
- **Incluir a barra `t` no cálculo do máximo/mínimo** — rejeitado: embaralha decisão e formação da barra, enfraquece a legibilidade causal do código da estratégia mesmo sem violar o engine.
- **Janela única simétrica (`window` único, mesmo valor para entrada e saída)** — rejeitado: 20/10 (Turtle) é o uso clássico e mais informativo para o laboratório; simetria 20/20 seria decisão arbitrária de simplificação.
- **Forçar `entry_window >= exit_window` no construtor** — rejeitado: restrição sem motivo estrutural; configurações assimétricas ao contrário (10/20) são defensáveis como hipótese de estratégia e não quebram nenhum contrato.
- **Aceitar `float`-que-é-inteiro (`20.0`) no construtor** — rejeitado: abre porta para bug sutil de ponto flutuante; validação rigorosa de tipo é padrão do projeto desde ADR-0008.
- **Defaults `(20, 10)` no construtor** — rejeitado: defaults no construtor deixam callers programáticos errarem silenciosamente; defaults vivem apenas na CLI.
- **Estratégia com estado mínimo (`self._last_signal` ou similar)** — rejeitado: duplica responsabilidade do engine e cria fonte de divergência silenciosa. Stateless absoluto é o padrão da família de estratégias.
- **Priorizar `ENTER_LONG` sobre `EXIT` na barra de reversão simultânea** — rejeitado: "preferir ficar dentro" é decisão de estratégia, não de contrato. `EXIT` antes é a arbitragem mais conservadora e legível.
- **Emitir `HOLD` quando entrada e saída disparam simultaneamente** — rejeitado: encobre informação; o engine deve receber sinal acionável e decidir baseado no estado de posição.
- **Reutilizar `--short-window`/`--long-window` da MA para os parâmetros do Donchian** — rejeitado: nomes mentem (Donchian não tem "short/long MA"); flags dedicadas (`--entry-window`/`--exit-window`) são mais claras ao custo de mais duas linhas no `--help`.
- **Agrupar parâmetros em `--strategy-params entry=20,exit=10`** — rejeitado: parsing ad-hoc, tipagem frágil, perde tab-completion e `--help` automático.
- **`run-demo` rodar dois backtests lado a lado (MA vs Donchian) com output comparativo** — rejeitado nesta fase: fura o princípio atual de "um backtest por invocação". Comparação lado a lado é trabalho de `ranking/reporting/`.
- **Caracterizar primeiro no sintético seminal para manter consistência com ADR-0008** — rejeitado: sintético atual é drift-baixo + ruído Gaussiano, regime anti-breakout; caracterização sobre ele seria pouco informativa. Dataset real já está disponível (ADR-0009) e é mais apropriado para esta família.
- **Integration test dedicado ao Donchian em `tests/integration/`** — rejeitado nesta fase: o `run-demo` de caracterização exercita o fluxo end-to-end; `test_first_real_dataset.py` já cobre o loop completo com outra estratégia; adicionar integration dedicado seria redundante.
- **Replicar property-based de monotonicidade de custo (ADR-0010) para Donchian já nesta ADR** — rejeitado: trabalho mecânico; fica como follow-up explícito, não como penduricalho implícito da ADR-0011.
- **Parametrizar testes unitários com múltiplos `(entry_window, exit_window)`** — rejeitado: esconde intenção por trás de IDs de pytest; padrão ADR-0008 usa classes nomeadas explícitas, mais verbosas mas muito mais legíveis em revisão.
- **Discussão genérica de "por que breakout funciona em cripto" na ADR** — rejeitado: hipótese de mercado, não decisão arquitetural; o laboratório deve testar, não defender textualmente.

## Follow-ups

Concrete actions this decision creates. Each one belongs in `STATE.md` as pending work.

- Implementar `src/alpha_forge/strategies/families/donchian/__init__.py` + `strategy.py` conforme §"Regra exata" e §"Contrato de parâmetros".
- Implementar `tests/unit/test_donchian_breakout.py` com classes nomeadas: `TestValidacaoParametros`, `TestWarmUp`, `TestEntradaBreakoutAlta`, `TestSaidaBreakoutBaixa`, `TestArbitragemReversao` (com nome/comentário explícito de caso artificial), `TestIgnoraBarraCorrente` (mutando `high`, `low` e `close` de `window.iloc[-1]`, não só um campo), `TestLongOnly` (provando que a estratégia nunca emite sinal fora do contrato permitido, não só `HOLD`), `TestStateless`.
- Implementar `tests/property/test_donchian_causal.py` com `entry_window=5, exit_window=3`; gerador respeitando invariantes mínimos de OHLC (`high >= max(open, close, low)`, `low <= min(open, close, high)`).
- Atualizar `src/alpha_forge/cli/app.py`: adicionar `donchian` ao enum `--strategy`, adicionar `--entry-window` e `--exit-window` com defaults 20/10, estender `_build_strategy` e `_strategy_param_label`. Atualizar `--help` deixando claro quais flags pertencem a qual estratégia.
- Rodar suíte completa, confirmar verde sem flakiness.
- Rodar `run-demo` com `--strategy donchian --dataset-id btcusdt_1h_20250705_20251231_binance_spot` e capturar o output bruto.
- Atualizar `system/domain.md` (nova entidade), `system/api.md` (novo módulo + flags + `--help`), `system/flows.md` (output de caracterização no dataset real, com nota explícita "observação, não validação") e `STATE.md`.
- **Follow-up explícito, não nesta entrega:** replicar ADR-0010 (property-based de monotonicidade de custo) para Donchian quando decidido — teste paralelo, não parametrização, cada estratégia explícita.
- **Não** tocar em `validation/`, `ranking/`, `regimes/`, ou `vectorbt`. ADR-0011 é estritamente camada de estratégia + CLI + testes + docs.
