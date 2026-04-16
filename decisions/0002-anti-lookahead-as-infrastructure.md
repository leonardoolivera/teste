# 0002 — Política anti-lookahead como regra de infraestrutura (núcleo mínimo)

**Status:** Accepted
**Date:** 2026-04-16
**Deciders:** Usuário (owner do projeto) + agente.

## Context

Lookahead bias é o erro silencioso mais caro em pesquisa quantitativa: resultados lindos em backtest, performance real catastrófica. `vision/01-product.md` elevou "sem lookahead, nunca" a princípio do produto. ADR-0001 registrou direção macro para `vectorbt` como motor de backtest, mas o núcleo mínimo ainda não usa vectorbt — usa um loop causal próprio, simples e auditável, que cabe nesta fase de bootstrap.

Promessa do autor ("eu jurei que não há lookahead") não é política executável. Precisamos que a ausência de lookahead seja **verificável por infraestrutura**, não por disciplina.

## Decision

Anti-lookahead no Alpha Forge é **enforcement de infraestrutura, não promessa do autor da estratégia**. O contrato do engine é desenhado para que trapaça estrutural seja difícil, não apenas detectável. Quatro regras obrigatórias, aplicadas desde o núcleo mínimo:

1. **Ordem temporal estrita.** Sinal gerado em barra `t` só pode usar dados de barras `<= t`. Execução do sinal ocorre em barra `t+1` (open da barra seguinte), nunca na mesma barra.
2. **Contrato estrutural de acesso a dados.** A estratégia **não recebe o dataset completo para decidir candle a candle**. Ela deve operar sob um dos dois contratos, nunca livre:
   - **Contrato A (janela causal):** a cada barra `t`, o engine entrega à estratégia apenas a fatia `data[:t+1]` (ou uma janela rolante causal), nunca o DataFrame inteiro acessível por índice arbitrário.
   - **Contrato B (sinais pré-computados + validação causal):** a estratégia emite uma série de sinais sobre o dataset completo, mas o engine **valida causalidade via `assert_causal` antes de executar qualquer ordem**. Violação → exceção, execução abortada.
   O autor da estratégia não ganha liberdade de inspecionar o futuro e depois prometer que não inspecionou.
3. **Guardião de lookahead obrigatório.** Um módulo `backtest/lookahead_guard.py` expõe `assert_causal(signal_series, price_series)` que verifica, via shift/align, que nenhum sinal usou informação futura. O engine chama essa função em **toda** execução de backtest, sem flag de desativação.
4. **Teste property-based obrigatório.** Pelo menos um teste com `hypothesis` constrói séries adversariais e confirma que o guardião detecta violações injetadas artificialmente (peek, shift negativo, uso de `close[t]` como sinal em `t`).

**Nota sobre compatibilidade com ADR-0001:** o motor próprio do núcleo mínimo é uma **escolha tática inicial**, não substituição da direção macro para `vectorbt`. Quando o volume de estratégias/combinações justificar (fase `building` avançada), o engine próprio será substituído/adapatado para rodar sobre `vectorbt`, mantendo as mesmas três regras como contrato. Esta ADR não revoga ADR-0001.

## Consequences

- **Positive:** qualquer violação de causalidade é detectada automaticamente, mesmo em estratégia nova; o contrato de temporalidade é explícito e testável; a transição futura para vectorbt herda o mesmo contrato.
- **Negative:** overhead de verificação em cada backtest (aceitável: o custo é baixo no núcleo mínimo); uma estratégia legítima que por erro tenta usar close de `t` para decisão em `t` é rejeitada — é exatamente o comportamento desejado, mas custa tempo de debug inicial.
- **Neutral:** a regra "execução em `t+1` open" simplifica custo/slippage para o núcleo mínimo; refinamentos (limit orders, partial fills) ficam `deferred`.

## Alternatives considered

- **Confiar no autor da estratégia** — rejeitado: a história de pesquisa quantitativa é feita de autores confiáveis enganados por si mesmos.
- **Validação apenas por review de código** — rejeitado: não escala quando houver dezenas de famílias de estratégia e variações.
- **Adiar guardião até o vectorbt** — rejeitado: a regra deve existir desde a primeira estratégia; adiar cria dívida técnica e resultados contaminados que teriam que ser refeitos.
- **Permitir execução na mesma barra sob flag** — rejeitado para esta fase: flag opcional vira flag esquecida; retornar a esse debate apenas se houver caso de uso concreto (ex.: modelos intrabar).

## Follow-ups

- Implementar `src/alpha_forge/backtest/lookahead_guard.py` com `assert_causal(signals, prices)`.
- Integrar a chamada ao guardião no `backtest/engine.py` como etapa obrigatória antes de computar equity.
- Escrever `tests/property/test_lookahead_guard.py` usando `hypothesis` para gerar séries adversariais.
- Escrever `tests/unit/test_lookahead_guard.py` com caso positivo (sinal causal passa) e negativo (sinal com peek falha com exceção clara).
- Quando o motor migrar para vectorbt (fase futura), abrir ADR de superseção parcial documentando como as três regras são preservadas no novo motor.
