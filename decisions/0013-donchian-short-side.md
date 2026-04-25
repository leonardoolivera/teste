# 0013 — Donchian breakout: habilitar short side (long+short simétrico)

**Status:** Accepted
**Date:** 2026-04-17
**Deciders:** Usuário (owner do projeto, autorização autônoma explícita) + agente.

## Context

ADR-0011 entregou `DonchianBreakoutStrategy` **long-only por decisão explícita** (§"Fica explicitamente fora desta ADR", item 1: "Short side. Mesma postura de ADR-0008: long-only nesta fase. Short vira ADR própria quando fizer sentido operacional, não como penduricalho"). ADR-0012 entregou short side para MA crossover + reverse-on-signal no engine (`_apply_signal_at_next_open` passou a suportar `posição aberta + sinal oposto → fecha + reabre em t+1 open, custo duplo`). O laboratório amadureceu:

- O engine suporta reverse-on-signal end-to-end, testado por `tests/property/test_engine_reverse_on_signal.py` (regressão dura do caminho long-only) e por caracterização multi-asset da MA simétrica em `system/flows.md`.
- O modo simétrico da MA tem property-based de monotonicidade de custo próprio (ADR-0010 aplicada ao modo `long_only=False`), fechando o follow-up explícito da ADR-0012.
- A caracterização multi-asset da Donchian long-only mostrou hit_rate na faixa de 25–31% nos três ativos — perfil típico de breakout ("poucos trades vencedores grandes teriam que compensar muitos perdedores pequenos"). SOL fechou `−8.80% / −14.55% drawdown`, exatamente o regime em que short é a contraparte natural do breakout bilateral.

Ativar short na Donchian nesta fase é **baixíssimo custo arquitetural**:

- Engine já suporta reverse-on-signal (ADR-0012). Nada novo precisa ser adicionado em `engine.py`.
- `Signal.ENTER_SHORT` já tem primeiro consumidor real (MA); segundo consumidor não exige mudança de domínio.
- O contrato de breakout é **simétrico por natureza**: `high[t-1] > max(prior_highs)` é breakout bullish; `low[t-1] < min(prior_lows)` é breakout bearish. Hoje o breakout bearish é `EXIT`; o modo simétrico o transforma em `ENTER_SHORT`.

O que **não** é decisão arquitetural nova é "short funciona em cripto" (hipótese de mercado). O que **é** decisão: como expressar a simetria sem quebrar o contrato ADR-0011 e sem ativar short silenciosamente para callers existentes.

## Decision

Adicionar um terceiro parâmetro `long_only: bool` ao construtor de `DonchianBreakoutStrategy`, com **default `True`** (preserva integralmente o comportamento ADR-0011 para callers existentes). Quando `long_only=False`, a estratégia emite `ENTER_SHORT` no breakout bearish a partir de posição plana, e as reversões são coordenadas pelo engine via reverse-on-signal (ADR-0012).

### Regra exata (parte da decisão)

Dados `window = prices[:t+1]`, parâmetros `entry_window`, `exit_window` e `long_only`:

**Eventos observáveis na barra `t`** (inalterados vs ADR-0011):

- **Breakout bullish** quando `high[t-1] > max(high[t-entry_window-1 : t-1])`.
- **Breakout bearish** quando `low[t-1] < min(low[t-exit_window-1 : t-1])`.
- Desigualdades estritas: empate exato **não** dispara sinal.
- A janela de comparação exclui `t-1` (é o máximo/mínimo das `N` barras anteriores a `t-1`).
- Warm-up: `HOLD` enquanto `len(window) < max(entry_window, exit_window) + 2`.

**Mapeamento de sinal (depende de `long_only`):**

| `long_only` | Breakout bullish → | Breakout bearish → | Ambos simultâneos → |
| --- | --- | --- | --- |
| `True` (default) | `ENTER_LONG` | `EXIT` | `EXIT` (regra ADR-0011 §"ordem EXIT→ENTER") |
| `False` | `ENTER_LONG` | `ENTER_SHORT` | `ENTER_SHORT` (ver justificativa abaixo) |

**Justificativa para "ambos simultâneos → ENTER_SHORT no modo simétrico":**

- ADR-0011 resolveu a barra dupla priorizando `EXIT` (arbitragem conservadora, "prefere sair"). Consistência com aquele princípio exige arbitragem conservadora análoga no modo simétrico.
- No modo simétrico não há `EXIT` explícito — o fechamento é via reversão. Se ambos rompimentos disparam na mesma barra, a última informação cronológica é a perda do mínimo (breakout bearish). Emitir `ENTER_SHORT` coloca o trader no lado bear e deixa o engine coordenar (fecha long se houver, abre short).
- Alternativa `ENTER_LONG` foi rejeitada porque subordinaria a informação de baixa à de alta sem razão estrutural. Alternativa `HOLD` foi rejeitada porque esconde informação — o engine deve receber sinal acionável.
- Nota: barras com ambos rompimentos são raras (exigem range explosivo em `t-1`) e qualquer escolha aqui tem efeito de segunda ordem; a regra fica explícita para não ficar "por acaso".

No modo simétrico (`long_only=False`), **não há `EXIT` explícito da Donchian**. O fechamento de uma posição ocorre via reversão: estar comprado e receber `ENTER_SHORT` produz fechamento e reabertura na outra direção, coordenados pelo engine (ADR-0012, reverse-on-signal, custo duplo).

### Contrato de parâmetros (parte da decisão)

Validação cedo no `__init__`, mesmo rigor de ADR-0008, ADR-0011 e ADR-0012:

- `entry_window` e `exit_window`: inalterados (`int` verdadeiro, `bool` rejeitado, `> 0`).
- `long_only`: deve ser `bool` estrito (rejeita `int`, `None`, `"true"`). Violação → `TypeError`. Default `True`. Ordem posicional: `(entry_window, exit_window, long_only=True)`; callers existentes com dois argumentos posicionais seguem funcionando sem qualquer mudança.
- Parâmetros congelados no `__init__`.

### Separação estratégia × engine (parte da decisão)

- `decide(window) -> Signal` continua puro e stateless. O sinal emitido em cada barra depende apenas de `window`, `entry_window`, `exit_window` e `long_only`.
- A estratégia **não** conhece o estado de posição do engine. No modo `long_only=False`, ela emite `ENTER_SHORT` em breakout bearish mesmo quando o engine está plano (primeiro short é legítimo, espelhando o primeiro long em breakout bullish).
- Reverse-on-signal é **responsabilidade do engine** (ADR-0012), não da estratégia. Estratégia emite um único sinal por barra.
- **Engine não é alterado nesta ADR.** ADR-0012 já entregou reverse-on-signal de forma genérica; ADR-0013 apenas ganha um segundo consumidor (Donchian além da MA).

### Integração com CLI (parte da decisão)

- A flag `--long-only / --no-long-only` já existe (ADR-0012). Nesta ADR ela passa a afetar **também** `--strategy donchian`.
  - `--long-only` (default): Donchian long-only (comportamento ADR-0011).
  - `--no-long-only`: Donchian simétrico.
- Summary passa a imprimir `strategy: donchian entry=20 exit=10 long_only=True` (ou `False`).
- `--help` é atualizado: remove qualificação "`--no-long-only` só afeta `ma_crossover`" (ADR-0012) e passa a listar `{ma_crossover, donchian}` como estratégias que honram a flag.

### Caracterização inicial (parte da decisão)

Caracterizar em três ativos (BTC, ETH, SOL) com `entry_window=20, exit_window=10, long_only=False`, comparando com os resultados long-only já registrados em `system/flows.md` (Output exemplo 4 e 5). A caracterização é **observação**, não validação — mesma postura de ADR-0009, ADR-0011 e ADR-0012. Juízo de edge fica fora.

## Consequences

- **Positive:** Donchian deixa de "perder metade da ação" em recortes com downtrend; reutiliza integralmente reverse-on-signal da ADR-0012 sem nova complexidade no engine; o contrato `long_only: bool` vira padrão estável do laboratório (MA + Donchian); callers existentes (tests, integration, CLI default) continuam idênticos por causa do default `True`; CLI fica mais coesa — a mesma flag agora cobre as duas famílias simétricas.
- **Negative:** superfície de teste da Donchian dobra (precisa de `tests/unit/test_donchian_short.py` espelhando a estrutura de `test_ma_crossover_short.py`); property-based de monotonicidade de custo no modo simétrico vira follow-up explícito (`tests/property/test_cost_monotonicity_donchian_short.py` — quarto arquivo paralelo); custo duplo na reversão que já existe para MA passa a acontecer também para Donchian, o que pode surpreender leitor desavisado — precisa ser documentado.
- **Neutral:** o universo de estratégias simétricas do laboratório vira duas (MA + Donchian); RSI ou mean-reversion futuros herdam o padrão sem nova ADR de engine; o enum `Signal.ENTER_SHORT` ganha segundo consumidor real.

### Fica explicitamente fora desta ADR

1. **Stops, targets, filtros direcionais.** Entrada e reversão são por breakout; nada de "short só se volatilidade > X".
2. **Sizing assimétrico por direção.** `RiskBudget` continua único; short usa o mesmo `fracao_por_trade` e `alavancagem_max` do long.
3. **Trailing logic para trocar `long_only` em runtime.** O parâmetro é congelado no `__init__`.
4. **Replicar property-based de monotonicidade (ADR-0010) para o modo Donchian simétrico.** Follow-up explícito, não parte da entrega; arquivo paralelo `tests/property/test_cost_monotonicity_donchian_short.py`.
5. **Alterar assinatura pública do `run_backtest` ou `BacktestResult`.** Engine **não** é alterado; ADR-0013 é estritamente camada de estratégia + CLI + testes + docs + caracterização.
6. **Unificar contrato `long_only` em um mixin ou ABC.** Tentador, mas premature abstraction: duas famílias ainda é pouco para justificar. Se uma terceira simétrica entrar, reavalia-se.
7. **Janelas separadas para breakout bullish vs bearish (ex: `entry_window_long` + `entry_window_short`).** Rejeitado: Donchian clássico usa as mesmas janelas para ambos; assimetria é hipótese de estratégia, não decisão estrutural.

### Critério de sucesso

ADR-0013 está **concluída** quando:

- `DonchianBreakoutStrategy.__init__` aceita `long_only: bool = True`, com validação estrita de tipo.
- `decide(window)` emite `ENTER_SHORT` em breakout bearish quando `long_only=False`; emite `EXIT` em breakout bearish quando `long_only=True` (comportamento ADR-0011 preservado bit-a-bit).
- Engine **não** é alterado (reverse-on-signal da ADR-0012 cobre o caso).
- Bateria unit em `tests/unit/test_donchian_short.py` passa em verde (suite nova, não tocar `test_donchian_breakout.py`):
  - `TestDefaultPreservaLongOnly` (default comprovadamente comporta-se como ADR-0011).
  - `TestValidacaoLongOnly` (rejeita `int`, `None`, `str`).
  - `TestSimetriaSinais` (breakout bullish → `ENTER_LONG`; breakout bearish → `ENTER_SHORT` no modo simétrico; ambos simultâneos → `ENTER_SHORT`; warm-up respeitado).
  - `TestLongToShort` (integração engine + estratégia numa série construída com reversão sucessiva; fills com `Side.LONG`/`Side.SHORT`/`Side.FLAT`; custo duplo reduz equity vs zero-cost).
  - `TestStateless` (duas chamadas = mesmo resultado).
- Regressão dura do caminho ADR-0011: `test_donchian_breakout.py` e `test_donchian_causal.py` **não tocados** e continuam verdes. O property-based existente `test_engine_reverse_on_signal.py` já cobre a garantia de que engine em long-only segue bit-idêntico.
- CLI: `--no-long-only --strategy donchian` funciona, summary reflete corretamente, `--help` documenta.
- Caracterização real 3×1 (BTC/ETH/SOL, Donchian 20/10, `long_only=False`) em `system/flows.md` como Output exemplo 7, com nota explícita "observação, não validação".
- `system/domain.md`, `system/api.md`, `system/flows.md`, `STATE.md`, `decisions/README.md` refletem a mudança.

Fora do critério de sucesso: qualquer alvo numérico de PnL, hit_rate ou drawdown; qualquer comparação que sustente "short é melhor" ou pior que long-only em Donchian.

## Alternatives considered

- **Criar classe nova `DonchianBreakoutSymmetric` em módulo separado** — rejeitado: duplicaria 90% do código, dobraria pontos de manutenção da regra de breakout, e introduziria divergência silenciosa quando uma evoluísse. Um parâmetro `long_only` é a expressão natural da simetria (mesma decisão de ADR-0012).
- **Default `long_only=False`** — rejeitado: quebra comportamento de callers existentes silenciosamente (testes, integration, CLI default, notebooks). ADR-0011 é contrato público; o default preserva esse contrato.
- **Emitir `ENTER_SHORT` mesmo no modo `long_only=True`, mas confiar no engine para filtrar** — rejeitado: viola princípio "sinal é semântica da estratégia, não do engine" (ADR-0008 §7, ADR-0012).
- **"Ambos rompimentos simultâneos → ENTER_LONG no modo simétrico"** — rejeitado: subordinaria a informação de baixa à de alta sem razão estrutural; quebra simetria com a arbitragem EXIT→ENTER do ADR-0011.
- **"Ambos rompimentos simultâneos → HOLD no modo simétrico"** — rejeitado: esconde informação acionável; engine deve receber sinal concreto.
- **Renomear a flag CLI para `--long-only-ma` / adicionar nova `--long-only-donchian`** — rejeitado: fragmenta a interface por estratégia sem razão estrutural; a flag boolean única `--long-only` cobre todas as estratégias simétricas com a mesma semântica.
- **Adicionar argumento keyword-only** (`*, long_only=True`) — rejeitado: cosmético; quebraria callers de três argumentos posicionais sem razão forte (mesma decisão de ADR-0012).
- **Criar mixin `SymmetricCapableStrategy` + ABC** — rejeitado: premature abstraction; duas famílias ainda é pouco para justificar. Reavaliar quando uma terceira entrar.
- **Aproveitar a ADR para adicionar filtro de regime (ex: só short se ADX > X)** — rejeitado: `regimes/` é `vision/`, não realidade; filtros são responsabilidade de ADR dedicada quando `regimes/` abrir.
- **Caracterizar primeiro no sintético seminal** — rejeitado: sintético é drift-baixo + ruído Gaussiano, regime anti-breakout por construção; caracterização sobre ele seria pouco informativa (mesma justificativa de ADR-0011 §"Caracterização inicial").
- **Replicar property-based de monotonicidade (ADR-0010) no modo simétrico dentro desta ADR** — rejeitado: trabalho mecânico; fica como follow-up explícito, não penduricalho implícito.
- **Janelas separadas para bullish vs bearish** — rejeitado: Donchian clássico usa as mesmas janelas; assimetria é hipótese de estratégia.

## Follow-ups

Concrete actions this decision creates. Each one belongs in `STATE.md` as pending work.

- Estender `src/alpha_forge/strategies/families/donchian/strategy.py` com parâmetro `long_only: bool = True`, validação estrita, e novo mapeamento de sinal no `decide`.
- Criar `tests/unit/test_donchian_short.py` (suite nova, não tocar `test_donchian_breakout.py`): `TestDefaultPreservaLongOnly`, `TestValidacaoLongOnly`, `TestSimetriaSinais`, `TestLongToShort`, `TestStateless`.
- Estender `src/alpha_forge/cli/app.py`: propagar `--long-only/--no-long-only` também para `donchian` em `_build_strategy`; atualizar `_strategy_param_label` para incluir `long_only=...` no summary da Donchian; atualizar help text.
- Rodar suíte completa, confirmar verde sem flakiness. `test_donchian_breakout.py` e `test_donchian_causal.py` **não** devem ser tocados e devem continuar verdes.
- Rodar `run-demo` em BTC/ETH/SOL com `--strategy donchian --no-long-only --entry-window 20 --exit-window 10`, capturar outputs.
- Atualizar `system/domain.md` (novo parâmetro na entidade Donchian, regra simétrica, arbitragem "ambos simultâneos → ENTER_SHORT"), `system/api.md` (flag `--long-only` agora cobre Donchian; assinatura atualizada), `system/flows.md` (Output exemplo 7 com tabela 3-asset `long_only=False` para Donchian, nota sobre custo duplo), `STATE.md` e `decisions/README.md`.
- **Follow-up explícito, não nesta entrega:** property-based de monotonicidade de custo para o modo simétrico (`long_only=False`) da Donchian — teste paralelo `tests/property/test_cost_monotonicity_donchian_short.py`, mesmo formato dos três anteriores (MA long-only, Donchian long-only, MA simétrico).
- **Não** tocar em `validation/`, `ranking/`, `regimes/`, `vectorbt`, ou `backtest/engine.py`. ADR-0013 é estritamente camada de estratégia + CLI + testes + docs.
