# 0012 — MA crossover: habilitar short side (long+short simétrico)

**Status:** Accepted
**Date:** 2026-04-16
**Deciders:** Usuário (owner do projeto) + agente.

## Context

ADR-0008 entregou `MovingAverageCrossoverStrategy` **long-only por decisão explícita** ("menos superfície de bug; hit rate e drawdown mais simples de auditar; short entra em ADR futura, caso o roadmap exija — não antes"). O laboratório desde então amadureceu: ADR-0009 trouxe dataset real BTCUSDT 180d, ADR-0010 cristalizou o contrato de custo com property-based, ADR-0011 adicionou segunda família (Donchian) e reforçou o padrão stateless + validação cedo + EXIT→ENTER na arbitragem. A ingestão multi-asset (BTC + ETH + SOL) caracterizou a MA long-only em três ativos e confirmou o que ADR-0008 §"Consequences/Negative" previa textualmente: long-only em cripto "perde metade da ação". Em SOL a MA long-only fechou −6.85% no recorte, consistente com um recorte dominado por downtrend — exatamente o regime em que short é a contraparte natural.

Ativar o short side nesta fase é baixo custo arquitetural e alto valor observacional:

- O engine já suporta `Side.SHORT` end-to-end ([engine.py:174](../src/alpha_forge/backtest/engine.py#L174), [engine.py:241](../src/alpha_forge/backtest/engine.py#L241)): sizing, cost model, PnL por direção, mark-to-market. Nada de infraestrutura precisa ser adicionado.
- O enum `Signal.ENTER_SHORT` já existe desde o domínio seminal; a MA simplesmente não o emitia.
- O contrato de cruzamento é **simétrico por natureza matemática**: o cruzamento para baixo, que hoje é `EXIT`, é exatamente o sinal de entrada short em uma versão simétrica.

O que **não** é decisão arquitetural nova é "short faz sentido em cripto" (hipótese de mercado, não decisão de laboratório). O que **é** decisão: como expressar o contrato simétrico sem quebrar o contrato ADR-0008 e sem ativar short silenciosamente para callers existentes.

## Decision

Adicionar um terceiro parâmetro `long_only: bool` ao construtor de `MovingAverageCrossoverStrategy`, com **default `True`** (preserva integralmente o comportamento ADR-0008 para callers existentes). Quando `long_only=False`, a estratégia emite `ENTER_SHORT` no cruzamento para baixo a partir de posição plana, e o `EXIT` do lado long/short continua sendo o cruzamento inverso correspondente.

### Regra exata (parte da decisão)

Dados `short_ma[t]`, `long_ma[t]`, `short_ma[t-1]`, `long_ma[t-1]` sobre `window = prices[:t+1]`:

**Eventos observáveis na barra `t`:**

- **Cross-up** quando `short_ma[t] > long_ma[t]` **e** `short_ma[t-1] <= long_ma[t-1]`.
- **Cross-down** quando `short_ma[t] < long_ma[t]` **e** `short_ma[t-1] >= long_ma[t-1]`.
- Empate numérico exato (`==`) **não** dispara cross. Inequalidade estrita em `t` + `<=`/`>=` em `t-1` capturam corretamente cruzamento que começa de empate (contrato idêntico a ADR-0008 §4, reafirmado).

**Mapeamento de sinal (depende de `long_only`):**

| `long_only` | Cross-up → | Cross-down → |
| --- | --- | --- |
| `True`  (default) | `ENTER_LONG` | `EXIT` |
| `False` | `ENTER_LONG` | `ENTER_SHORT` |

No modo simétrico (`long_only=False`), **não há `EXIT` explícito da MA**. O fechamento de uma posição ocorre via reversão: estar comprado e receber `ENTER_SHORT` produz fechamento e reabertura na outra direção, coordenados pelo engine. Isso é comportamento coerente com a natureza do cruzamento simétrico: o mesmo evento que fecharia o long é o que abre o short.

**Importante — modelo de reversão:** o engine **não** implementa hoje "fechar e reabrir em um único tick". Na arquitetura atual ([engine.py:156-171](../src/alpha_forge/backtest/engine.py#L156-L171)): se há posição aberta e chega `ENTER_LONG`/`ENTER_SHORT`, o sinal é no-op (engine só entra a partir de `Side.FLAT`). Portanto, no modo `long_only=False`, quando long+ENTER_SHORT chega, o engine **ignora** o sinal e a posição long permanece — até a próxima cross-up? Não, porque cross-up só dispararia após cross-down. Isto é um bug semântico inaceitável.

**Duas alternativas para resolver, dentro desta ADR:**

1. **Reverse-on-signal no engine:** ampliar `_apply_signal_at_next_open` para que, se o sinal de entrada chega contra uma posição aberta de sinal oposto, feche primeiro e reabra em seguida, tudo em `t+1 open`, com dois fills e um trade fechado (os custos são aplicados duas vezes, o que é fiel à realidade).
2. **Estratégia emite EXIT explícito na barra anterior:** inviável sem estado ou lookahead — a reversão é pontual, não há "barra anterior" acionável.

**Decisão:** seguir a rota (1) — ampliar o engine para suportar reverse-on-signal, restrito ao caso `posição != FLAT` **e** `signal ∈ {ENTER_LONG, ENTER_SHORT}` **e** `signal.side != position.side`. Nenhum outro fluxo muda.

### Contrato de parâmetros (parte da decisão)

Validação cedo no `__init__`, mesmo rigor de ADR-0008 e ADR-0011:

- `short_window` e `long_window`: inalterados (`int` verdadeiro, `bool` rejeitado, `0 < short_window < long_window`).
- `long_only`: deve ser `bool` estrito (rejeita `int`, `None`, `"true"`). Violação → `TypeError`. Default `True`. Ordem posicional: `(short_window, long_window, long_only=True)`; callers existentes com dois argumentos posicionais seguem funcionando sem qualquer mudança.
- Parâmetros congelados no `__init__`.

### Separação estratégia × engine (parte da decisão)

- `decide(window) -> Signal` continua puro e stateless. O sinal emitido em cada barra depende apenas de `window`, `short_window`, `long_window` e `long_only`.
- A estratégia **não** conhece o estado de posição do engine. No modo `long_only=False`, ela emite `ENTER_SHORT` em cross-down mesmo quando o engine está plano (primeiro short é legítimo) — exatamente o comportamento espelhado do `ENTER_LONG` original em cross-up.
- Redundância de sinais (ex: cross-up imediatamente após outro cross-up, improvável mas teoricamente possível em janela degenerada) continua sendo no-op do engine.
- Reverse-on-signal é **responsabilidade do engine**, não da estratégia. A estratégia não emite `EXIT` e depois `ENTER_SHORT` em barras separadas — emite um único sinal por barra.

### Mudança no engine (parte da decisão, escopo mínimo)

Em `_apply_signal_at_next_open`, substituir:

```python
if position.side != Side.FLAT:
    return
```

por uma lógica que:

1. Se `position.side == Side.FLAT`: comportamento atual (abre).
2. Se `position.side != Side.FLAT` **e** sinal de entrada na **mesma direção**: no-op (comportamento atual).
3. Se `position.side != Side.FLAT` **e** sinal de entrada na **direção oposta**: fecha posição atual **e** abre nova posição, ambas em `t+1 open`, custos aplicados duas vezes, um `Trade` fechado registrado, dois `Fill` registrados (um de fechamento, um de abertura), mesma `ts_exec` para ambos.

Essa mudança preserva 100% dos fluxos existentes — só adiciona um ramo para o caso novo.

### Integração com CLI (parte da decisão)

- Nova flag `--long-only / --no-long-only` (boolean flag padrão argparse):
  - `--long-only` (default, sem flag): comportamento ADR-0008.
  - `--no-long-only` (flag explícita): ativa short.
- Flag é silenciosamente ignorada quando `--strategy != ma_crossover`, mesmo padrão das demais.
- Summary passa a imprimir `strategy: ma_crossover short=20 long=50 long_only=True` (ou `False`).
- `--help` diz explicitamente que `--no-long-only` só afeta `ma_crossover` nesta ADR. Donchian permanece long-only por ADR-0011 §"Fica explicitamente fora".

### Caracterização inicial (parte da decisão)

Caracterizar em três ativos (BTC, ETH, SOL) com `short_window=20, long_window=50, long_only=False`, comparando com os resultados long-only já registrados em `system/flows.md`. A caracterização é **observação**, não validação — mesma postura de ADR-0009 e ADR-0011. O objetivo é ver se o modelo de reversão funciona mecanicamente e se o trade_count/hit_rate/max_drawdown mudam de forma coerente com a mudança de contrato. Juízo de edge fica fora.

## Consequences

- **Positive:** MA crossover deixa de "perder metade da ação" em recortes com downtrend; reverse-on-signal no engine desbloqueia estratégias simétricas futuras (RSI mean-reversion, por exemplo) sem nova ADR; o próprio contrato `long_only: bool` fica disponível para reutilização em famílias futuras; callers existentes (tests, integration, CLI default) continuam idênticos por causa do default `True`.
- **Negative:** engine ganha um ramo a mais (reverse-on-signal), aumentando superfície de teste e exigindo property-based para garantir que o ramo antigo não foi alterado; custos duplicados no tick de reversão podem surpreender leitor desavisado — precisa ser documentado em `system/flows.md`; modo short exige testes adicionais que cobrem sequências cross-up→cross-down→cross-up com transições de `FLAT`→`LONG`→`SHORT`→`LONG`.
- **Neutral:** Donchian segue long-only; se o usuário quiser short para Donchian, será ADR dedicada — ADR-0012 é estritamente para MA; o enum `Signal.ENTER_SHORT` passa a ter primeiro consumidor real (antes era só contrato).

### Fica explicitamente fora desta ADR

1. **Short side da Donchian.** Se fizer sentido, vira ADR dedicada. ADR-0012 não faz assumir-por-extensão.
2. **Stops, targets, filtros direcionais.** Entrada e reversão são por cruzamento; nada de "short só se volatilidade > X".
3. **Sizing assimétrico por direção.** `RiskBudget` continua único; short usa o mesmo `fracao_por_trade` e `alavancagem_max` do long.
4. **Trailing logic para trocar `long_only` em runtime.** O parâmetro é congelado no `__init__`.
5. **Replicar property-based de monotonicidade (ADR-0010) para o modo short.** Follow-up explícito, não parte da entrega.
6. **Alterar assinatura pública do `run_backtest` ou `BacktestResult`.** A mudança no engine é interna a `_apply_signal_at_next_open`; o contrato externo não muda.

### Critério de sucesso

ADR-0012 está **concluída** quando:

- `MovingAverageCrossoverStrategy.__init__` aceita `long_only: bool = True`, com validação estrita de tipo.
- `decide(window)` emite `ENTER_SHORT` em cross-down quando `long_only=False`; emite `EXIT` em cross-down quando `long_only=True` (comportamento ADR-0008 preservado bit-a-bit).
- Engine suporta reverse-on-signal: posição aberta + sinal de entrada oposta → fecha e reabre em `t+1 open`.
- Bateria unit em `tests/unit/test_ma_crossover_short.py` passa em verde (nova suite dedicada, para não tocar no arquivo existente que corresponde à ADR-0008):
  - `TestDefaultPreservaLongOnly` (default comprovadamente comporta-se como ADR-0008).
  - `TestValidacaoLongOnly` (rejeita `int`, `None`, `str`).
  - `TestSimetriaSinais` (cross-up → `ENTER_LONG`, cross-down → `ENTER_SHORT` no modo simétrico).
  - `TestLongToShort` (integração engine + estratégia numa série construída com duas reversões sucessivas).
- Bateria property-based em `tests/property/test_engine_reverse_on_signal.py`:
  - Para série arbitrária, se nenhum sinal de reversão é emitido, o resultado é **bit-idêntico** ao engine pré-ADR-0012 (regressão dura).
- CLI: `--no-long-only` funciona, summary reflete corretamente, `--help` documenta.
- Caracterização real 3×1 (BTC/ETH/SOL, MA 20/50, `long_only=False`) em `system/flows.md` com nota explícita "observação, não validação".
- `system/domain.md`, `system/api.md`, `system/flows.md`, `STATE.md`, `decisions/README.md` refletem a mudança.

Fora do critério de sucesso: qualquer alvo numérico de PnL, hit_rate ou drawdown; qualquer comparação que sustente "short é melhor" ou pior.

## Alternatives considered

- **Criar classe nova `MovingAverageCrossoverSymmetric` em módulo separado** — rejeitado: duplicaria 90% do código, dobraria pontos de manutenção do contrato causal, e introduziria divergência silenciosa quando uma das duas evoluísse. Um parâmetro `long_only` é a expressão natural da simetria.
- **Default `long_only=False`** — rejeitado: quebra comportamento de callers existentes silenciosamente (testes, integration, qualquer notebook). ADR-0008 é contrato público; o default preserva esse contrato.
- **Emitir `ENTER_SHORT` mesmo no modo `long_only=True`, mas confiar no engine para filtrar** — rejeitado: viola o princípio "sinal emitido deve ser semântica da estratégia, não do engine" (ADR-0008 §7). Filtro no engine cria brecha para o usuário esquecer a flag e receber shorts inesperados de outra estratégia.
- **Não mudar engine; fazer a estratégia emitir `EXIT` numa barra e `ENTER_SHORT` na próxima** — inviável sem estado interno e sem antecipar futuro; reversão é pontual na barra do cruzamento.
- **Reverse-on-signal via dois sinais em barras distintas no engine** — rejeitado: quebraria a propriedade "um sinal por barra, uma execução em `t+1 open`", que é fundamento do contrato causal.
- **Custos simples (única aplicação) na reversão** — rejeitado: fisicamente, reverter é duas operações de mercado (fechar + abrir); aplicar custo uma vez só subestimaria atrito de forma sistemática.
- **Sinais redundantes no modo simétrico (ex: `ENTER_LONG` recorrente enquanto já long)** — tratados idênticos ao ADR-0011: no-op no engine, zero mudança.
- **Adicionar argumento posicional em vez de keyword-only** — aceito: ordem `(short_window, long_window, long_only=True)`. Keyword-only seria cosmético e quebraria callers programáticos de três argumentos sem razão forte.
- **Reverter da CLI via duas flags separadas `--enable-short` + `--enable-long`** — rejeitado: cria estados inválidos expressáveis (ex: `--no-enable-long --no-enable-short`) e expressa simetria como combinação, não como propriedade única.
- **Mudar o enum `Signal` para incluir `REVERSE_TO_LONG` / `REVERSE_TO_SHORT`** — rejeitado: inflação de domínio; a semântica de reversão é do engine, não do contrato de sinal.
- **Substituir o contrato da ADR-0008 (em vez de estender)** — rejeitado: ADRs são imutáveis (AGENTS.md §6); ADR-0012 estende, não supersede. O long-only de ADR-0008 continua sendo o default consciente.

## Follow-ups

Concrete actions this decision creates. Each one belongs in `STATE.md` as pending work.

- Estender `src/alpha_forge/strategies/families/ma_crossover/strategy.py` com parâmetro `long_only: bool = True`, validação estrita, e novo ramo no `decide`.
- Estender `src/alpha_forge/backtest/engine.py` com reverse-on-signal em `_apply_signal_at_next_open` (fecha + reabre em `t+1 open`, custo duplo, um `Trade` fechado, dois `Fill`).
- Criar `tests/unit/test_ma_crossover_short.py` (suite nova, não tocar `test_ma_crossover.py`): `TestDefaultPreservaLongOnly`, `TestValidacaoLongOnly`, `TestSimetriaSinais`, `TestLongToShort`.
- Criar `tests/property/test_engine_reverse_on_signal.py`: para série arbitrária + estratégia arbitrária que **nunca** emite reversão (MA long-only é suficiente), resultado é bit-idêntico ao comportamento pré-ADR-0012 em `final_equity`, `len(fills)`, `len(trades)`. Regressão dura do caminho antigo.
- Estender `cli/app.py` com flag `--no-long-only` e propagação ao construtor; summary atualizado; help text explicando escopo.
- Rodar suíte completa, confirmar verde sem flakiness.
- Rodar `run-demo` em BTC/ETH/SOL com `--strategy ma_crossover --no-long-only --short-window 20 --long-window 50`, capturar outputs.
- Atualizar `system/domain.md` (novo parâmetro, regra simétrica), `system/api.md` (nova flag, nova assinatura), `system/flows.md` (tabela de caracterização 3-asset, nota sobre custo duplo na reversão), `STATE.md` e `decisions/README.md`.
- **Follow-up explícito, não nesta entrega:** property-based de monotonicidade de custo para o modo simétrico (`long_only=False`) — teste paralelo, mesmo formato da ADR-0010.
