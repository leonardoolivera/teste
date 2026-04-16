# 0008 — First real strategy: causal moving average crossover (long-only)

**Status:** Accepted
**Date:** 2026-04-16
**Deciders:** Usuário (owner do projeto) + agente.

## Context

Até aqui, a única estratégia executável no núcleo é `DummyAlternatingStrategy` — ruído sobre ruído, cuja única função foi provar que o pipeline causal anda. Com ADR-0006 (custos) e ADR-0007 (métricas) instalados, já temos o tripé mínimo para caracterizar uma estratégia real: contrato causal, atrito sentido no PnL, e quatro métricas que reagem a ele.

Falta substituir a dummy por uma **primeira estratégia real**. "Real" aqui não significa "boa" — significa **legível, auditável, com contrato claro e sem atalhos de lookahead**. É a cobaia a partir da qual todas as futuras estratégias herdam padrão de escrita e padrão de teste.

A escolha natural é moving average crossover. Motivos:

- É o crossover mais simples que existe, amplamente documentado e fácil de auditar por inspeção.
- Expõe explicitamente os três conceitos que toda estratégia séria terá que respeitar neste repo: **warm-up**, **estado mínimo de sinal anterior** e **decisão local à barra `t` com janela `prices[:t+1]`**.
- Não tem nenhum parâmetro exótico; pode ser coberto por property-based test sem explosão combinatória.
- Sai da dummy sem antecipar `validation/`, `ranking/` ou `regimes/`.

A ADR fixa o contrato da primeira estratégia real. O objetivo desta fase é **validar o contrato**, não maximizar retorno.

## Decision

### 1. Identidade

- **Nome do módulo:** `alpha_forge.strategies.families.ma_crossover`.
- **Classe:** `MovingAverageCrossoverStrategy(Strategy)`.
- **Parâmetros:** `short_window: int`, `long_window: int`, com `0 < short_window < long_window`. Validados na construção; violação → `ValueError`. Defaults recomendados para o demo: `short_window=20`, `long_window=50` (explícitos, sem constante mágica).
- **Tipo:** SMA (média aritmética simples sobre `close`), não EMA. SMA é o caso mais transparente e mais fácil de testar.
- **Fonte de preço:** coluna `close` do DataFrame recebido. Nunca `open`, `high`, `low` ou volume. Nenhum outro campo é lido.

### 2. Direcionalidade — **long-only nesta fase**

A primeira estratégia real **não emite `ENTER_SHORT`**. Decisão deliberada:

- Menos superfície de bug.
- Hit rate e drawdown ficam mais simples de auditar.
- Short entra em ADR futura, caso o roadmap exija — não antes.

Sinais permitidos: `ENTER_LONG`, `EXIT`, `HOLD`. O enum `Signal.ENTER_SHORT` continua existindo no domínio (é contrato do engine), mas esta estratégia não o usa.

### 3. Contrato causal

A estratégia recebe exclusivamente `prices[:t+1]` via `decide(window)`. Nenhum acesso ao DataFrame futuro, a variáveis globais, a arquivos, ou ao dataset completo. Este contrato já é garantido estruturalmente por `run_backtest` (ADR-0002) — a ADR reafirma aqui para que o contrato seja visível ao leitor da estratégia.

### 4. Definição exata do cruzamento

Dado `short_ma[t]` e `long_ma[t]` computados sobre a janela `window = prices[:t+1]` (último ponto inclusive):

- **Sinal de entrada (`ENTER_LONG`):**
  `short_ma[t] > long_ma[t]` **e** `short_ma[t-1] <= long_ma[t-1]`.
  Ou seja, cruzamento **para cima** ocorrido na última barra disponível.
- **Sinal de saída (`EXIT`):**
  `short_ma[t] < long_ma[t]` **e** `short_ma[t-1] >= long_ma[t-1]`.
  Cruzamento **para baixo** ocorrido na última barra disponível. Essa é a **única** regra de saída nesta fase — sem stops, sem targets, sem time stops.
- **Igualdade exata (`==`):** tratada como "não houve cruzamento ainda". A inequalidade estrita (`>` / `<`) evita sinais espúrios em empate numérico. A condição `<=` / `>=` no ponto anterior captura corretamente o cruzamento que começa de empate.
- **Qualquer outro estado:** `HOLD`.

A decisão é **local à barra `t`**: a estratégia olha apenas os dois últimos valores das MAs. Não mantém histórico próprio de sinais anteriores para a regra de cruzamento — o "cruzamento ocorreu agora" é observável só nas duas últimas posições das MAs. Isso elimina a necessidade de estado interno para a lógica de sinal.

### 5. Warm-up / período inválido

- Enquanto `len(window) < long_window`, **não há média longa confiável**. A estratégia devolve `HOLD`. Sem exceção, sem warning.
- Adicionalmente: enquanto `len(window) < long_window + 1`, não é possível avaliar cruzamento (precisa de `t` **e** `t-1`). Também `HOLD`.
- Este é **estado esperado**, não erro. Consumers não devem tratar warm-up como falha.

Nenhum sinal válido é produzido nas primeiras `long_window` barras. Consequência mensurável: trade_count máximo no dataset seminal de 720 barras com `long_window=50` é limitado às ~670 barras pós warm-up.

### 6. Estado interno da estratégia

- A lógica de cruzamento não exige estado — é função de `window`. Portanto `MovingAverageCrossoverStrategy` é **stateless** na prática. A regra "não está em posição ⇒ pode entrar; está em posição ⇒ EXIT ao cruzamento inverso" é responsabilidade do **engine**, que já mantém `position` interna (vide `run_backtest`). A estratégia só emite intenção; o engine suprime entradas quando já existe posição aberta e materializa `EXIT` apenas se havia posição.
- Essa separação é deliberada: evita duplicar estado entre engine e strategy, e mantém `decide(window) -> Signal` como função pura de `window` e parâmetros. Testável sem simulação de backtest.

### 7. Separação de responsabilidades (estratégia × engine)

A estratégia:

- **Não** calcula sizing.
- **Não** aplica custo.
- **Não** decide timestamp de execução.
- **Não** lê o manifesto, dataset, ou qualquer I/O.
- **Só** produz `Signal` com base em `window`.

O engine:

- Chama `strategy.decide(window)` em cada barra `t`.
- Ignora `ENTER_LONG` se já há posição aberta (mesmo side).
- Materializa `EXIT` apenas se há posição aberta; caso contrário, `EXIT` com posição FLAT é no-op.
- Executa em `t+1 open`, aplica `CostModel`, chama `fixed_fractional_position_sizing`, classifica rejections. Todo esse encanamento já existe e não muda por conta desta ADR.

### 8. Critério de sucesso desta fase

O objetivo desta estratégia **não é ser lucrativa**. O objetivo é:

1. Validar o contrato `Strategy` com uma implementação real (primeira fora da dummy).
2. Permitir medir comportamento com e sem custos sobre lógica não-ruidosa.
3. Servir de **padrão de escrita** para estratégias futuras — organização de arquivos, testes, documentação em `system/`.
4. Fornecer baseline contra o qual futuras estratégias (breakout, RSI, etc.) serão comparadas qualitativamente até `ranking/` existir.

Aceitação da fase: suíte verde incluindo testes novos específicos desta estratégia; `run-demo` aceita uma flag opcional de estratégia (`--strategy ma_crossover`) ou expõe um segundo subcomando; métricas (`total_pnl`, `trade_count`, `hit_rate`, `max_drawdown`) reportadas coerentemente; `system/domain.md` e `system/api.md` atualizados.

### 9. Escopo explícito **fora** desta ADR

Nada disso entra agora — cada item vira, se necessário, ADR futura:

- EMA, WMA, qualquer MA adaptativa.
- Short side.
- Stops (fixo, trailing, ATR-based), targets, time stops.
- Filtros de regime, filtros de volatilidade, filtros de volume.
- Pirâmide, DCA, ajuste dinâmico de tamanho.
- Mais de um par de janelas (grid de parâmetros).
- Otimização de hiperparâmetros, walk-forward, monte carlo.
- Comparação multi-estratégia formal (vive em `ranking/`).

## Consequences

- **Positive:** sai da dummy sem antecipar infra futura; estratégia 100% auditável por inspeção; contrato causal reafirmado no código real, não só na dummy; padrão de escrita fica estabelecido para futuras estratégias; property-based test cobre corretude do cruzamento em famílias de séries geradas por hypothesis.
- **Negative:** long-only sobre cripto perde a metade da ação; MA crossover sozinho é notoriamente pouco lucrativo em mercado lateral — esperar edge aqui é enganoso; usuário precisa resistir à tentação de tunar parâmetros antes de `validation/` existir.
- **Neutral:** escolher SMA (não EMA) é escolha de transparência, não de performance; exit apenas por cruzamento inverso significa que drawdowns podem ser profundos antes da saída — aceitável nesta fase pelo objetivo de validar contrato, não proteger capital.

## Alternatives considered

- **Long + short simétrico já nesta ADR** — rejeitado (sugestão do usuário e confirmada): dobra superfície de bug e dobra casos de teste para zero ganho na validação do contrato; short é ampliação natural em ADR futura.
- **EMA em vez de SMA** — rejeitado: EMA exige decisão sobre warm-up (usar EMA do próprio pandas com `adjust=False`? Seed com SMA? Primeiro valor?), e cada opção muda números sutilmente. SMA é aritmeticamente óbvia. EMA vira ADR própria se alguma futura estratégia exigir.
- **Adicionar um stop simples (ex.: -5% do preço de entrada)** — rejeitado: introduz parâmetro, introduz interação com custo, introduz ambiguidade sobre ordem de avaliação dentro da barra. Mantém contrato puro — stops entram em ADR separada quando for a hora.
- **Estratégia breakout (Donchian) como primeira** — rejeitado em favor de MA crossover por transparência matemática (média é mais óbvia que rolling max) e por MA ser a baseline histórica mais comum.
- **Emitir `ENTER_LONG` sempre que `short_ma > long_ma`, sem exigir cruzamento** — rejeitado: transforma a estratégia em filtro de regime, não em sinal de entrada; multiplica entradas espúrias; vai contra o espírito de "estratégia legível e auditável".
- **Estratégia manter o próprio estado "em posição ou não"** — rejeitado: duplica estado com o engine; abre brecha para inconsistência; viola o contrato `decide(window) -> Signal` como função pura.

## Follow-ups

- Implementar `src/alpha_forge/strategies/families/ma_crossover/__init__.py` expondo `MovingAverageCrossoverStrategy`, e `strategy.py` com a classe (pydantic-free; `__init__` simples com validação dos dois inteiros). Sem I/O no módulo.
- Escrever `tests/unit/test_ma_crossover.py`:
  - warm-up retorna `HOLD` para toda barra com `len(window) <= long_window`.
  - cruzamento construído analiticamente (série determinística que cruza na barra `t`) → `ENTER_LONG` em `t`, `HOLD` em `t-1` e em `t+1` (a menos que haja novo cruzamento).
  - cruzamento inverso → `EXIT`.
  - igualdade exata em `t` → `HOLD`, não sinal.
  - validação de parâmetros: `short_window >= long_window`, `short_window <= 0`, valores não-inteiros.
- Escrever `tests/property/test_ma_crossover_causal.py` (hypothesis): para toda série gerada, substituir a barra `t+1` por qualquer valor não muda o sinal em `t`. Garante que a estratégia é realmente função de `prices[:t+1]`, não de futuro.
- Atualizar `cli/app.py` para aceitar `--strategy {dummy,ma_crossover}` (default `ma_crossover` a partir desta ADR) e flags `--short-window`, `--long-window`. Imprimir a estratégia e parâmetros no summary.
- Rodar `run-demo` com a nova estratégia, zero cost vs custo padrão, e registrar em `system/flows.md` o novo output (substituindo ou complementando os outputs da dummy).
- Atualizar `system/domain.md` com a nova estratégia; `system/api.md` com o novo módulo e flags; `decisions/README.md` com esta ADR.
- Atualizar `STATE.md`: mover "ADR-0008 + MA crossover" de pending para "last delivered" ao concluir; próximo passo proposto ali.
