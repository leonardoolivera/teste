# LIGHTNING_SEARCH_PROTOCOL

**Nome operacional:** PROTOCOLO RAIO  
**Base metodologica:** `ROADMAP_ESTRATEGIAS_V2_METODOLOGICO.md`  
**Status:** desenho metodologico e operacional, nao executado  
**Escopo:** nao implementa codigo, nao roda backtests, nao altera estrategias, nao muda regras de risco.

## 1. Objetivo do protocolo

O PROTOCOLO RAIO converte o roadmap V2 em uma busca adaptativa em arvore para pesquisa de estrategias de trading. A execucao deixa de ser linear e passa a ser dirigida por evidencia incremental, custo de compute, risco de overfitting e valor marginal para o portfolio.

A logica central e:

- cada hipotese vira um no;
- cada variacao vira um filho;
- cada resultado decide se o no sera expandido, pausado, rebaixado, validado ou enterrado;
- a IA prioriza o melhor retorno esperado por unidade de esforco;
- nenhum galho recebe compute profundo sem sobreviver aos testes baratos;
- se um galho piorar, a IA retorna para a melhor bifurcacao anterior;
- hipoteses mortas ficam registradas para evitar reexecucao futura.

O protocolo nao substitui os criterios do roadmap V2. Ele define a ordem, profundidade, cortes e retorno entre bifurcacoes. O roadmap V2 diz "o que pode ser pesquisado"; o PROTOCOLO RAIO diz "como pesquisar sem desperdiclar compute nem minerar ruído".

## 2. Principio central

Principio obrigatorio:

> Testar pequeno, validar cedo, aprofundar apenas sobreviventes.

O protocolo deve evitar:

- roadmap linear cego;
- grid search excessivo;
- variacao parametrica sem hipotese;
- data snooping;
- overfitting por insistencia;
- compute caro em hipotese fraca;
- repeticao de hipoteses mortas;
- pergunta ao usuario sobre decisoes resolviveis por regra, documentacao, specs, ADRs ou estado da arvore.

## 3. Estrutura de arvore

Cada hipotese do roadmap V2 e representada como um no. Um no raiz representa uma tese estrutural. Um no filho representa uma mutacao controlada: outro ativo, outra janela, outro timeframe proximo, pequena variacao de parametro, outro exit ou filtro causalmente justificado.

Um filho nunca deve existir apenas porque "ainda nao testamos esse numero". Todo filho precisa declarar a mutacao em relacao ao pai e por que essa mutacao testa melhor o mecanismo causal.

### Schema obrigatorio de no

```yaml
node_id:
parent_id:
root_family:
tier:
status:
hypothesis:
causal_mechanism:
mutation_from_parent:
asset:
timeframe:
direction:
entry_logic:
exit_logic:
filters:
sizing:
data_window:
validation_level:
compute_cost_estimate:
result_summary:
metrics:
  net_return:
  max_drawdown:
  sharpe:
  sortino:
  calmar:
  profit_factor:
  expectancy:
  win_rate:
  payoff_ratio:
  trade_count:
  exposure:
  turnover:
  fees:
  slippage:
  worst_loss_streak:
  stability_by_window:
  stability_by_asset:
  stability_by_regime:
overfit_risk:
decision:
decision_reason:
next_children:
created_at:
updated_at:
```

### Status permitidos

| Status | Uso |
|---|---|
| CANDIDATE | No registrado, ainda nao testado. |
| SCOUTING | No em teste barato de nivel 1. |
| PROMISING | No passou scout ou replicacao inicial, mas ainda nao merece validacao cara. |
| EXPAND | No autorizado a gerar filhos limitados. |
| PAUSED | Bom conceito, mas bloqueado por custo, dependencia ou dados. |
| QUARANTINED | Resultado ambiguuo, baixo trade count, cauda suspeita ou dependencia externa. |
| REJECTED | Falhou criterio local, mas ainda nao foi registrado como morte definitiva. |
| SURVIVOR | Passou robustez suficiente para entrar em integracao ou falsificacao profunda. |
| VALIDATED | Passou escada completa ate nivel aplicavel. |
| GRAVEYARD | Hipotese enterrada; nao repetir sem excecao documentada. |

## 4. Niveis de validacao

### Nivel 0 - Idea Node

Objetivo: registrar a hipotese antes de testar.

Requisitos:

- hipotese clara;
- mecanismo causal plausivel;
- criterio de sucesso;
- criterio de invalidacao;
- custo estimado;
- risco de overfitting;
- parent_id definido, se nao for raiz;
- benchmark simples definido.

Regra: nao pode haver backtest sem registro previo do no. Se o no exigir codigo novo, dados adicionais, validacao estatistica ou ADR antes de producao, isso deve constar no registro.

### Nivel 1 - Scout Test

Objetivo: teste barato para detectar sinal inicial.

Escopo maximo:

- 1 ativo;
- 1 timeframe;
- 1 janela;
- 1 setup base;
- custos realistas;
- parametros minimos;
- sem busca extensa de threshold.

Critério para avancar:

- expectancy liquida positiva;
- trade_count suficiente, usando `>= 30` como minimo padrao quando a familia nao definir outro limiar;
- max drawdown toleravel para a familia;
- profit factor aceitavel, com `>= 1.10` como minimo inicial e `>= 1.20` preferido;
- resultado nao dependente de 1 ou 2 trades extremos;
- slippage realista nao destrói o resultado;
- mecanismo causal segue plausivel depois de ver os trades.

Se falhar claramente, mover para `GRAVEYARD`. Se for ambiguuo, mover para `QUARANTINED` ou repetir scout uma vez com uma unica alteracao justificada.

### Nivel 2 - Replication Test

Objetivo: verificar se o sinal nao e local.

Testar pelo menos um:

- outro ativo;
- outra janela temporal;
- outro timeframe proximo.

Critério para avancar:

- desempenho nao precisa ser perfeito;
- direcao do edge deve ser preservada;
- resultado nao pode colapsar completamente fora da janela original;
- trade_count agregado deve continuar suficiente;
- custos realistas continuam incluidos.

Se o no so funciona em um ativo e uma janela, ele so continua se essa especificidade tiver mecanismo causal forte e for marcada como risco alto.

### Nivel 3 - Sensitivity Test

Objetivo: testar robustez local.

Variações permitidas:

- parametros +/-10%;
- parametros +/-20%;
- threshold pequeno;
- janela proxima;
- exit levemente diferente;
- filtro equivalente, quando o mecanismo for o mesmo.

Critério para avancar:

- performance nao pode depender de um unico ponto parametrico;
- pequenas mudancas nao podem destruir totalmente o edge;
- drawdown nao pode explodir;
- a variacao nao pode virar nova hipotese escondida.

Se a hipotese colapsar com pequena perturbacao, mover para `GRAVEYARD` ou `QUARANTINED` se houver forte suspeita de problema de dados.

### Nivel 4 - Robustness Test

Objetivo: resistencia estatistica e operacional.

Incluir:

- fee stress;
- slippage stress;
- spread stress;
- latency stress, se aplicavel;
- Monte Carlo trade shuffle;
- walk-forward;
- out-of-sample;
- cross-era;
- cross-asset;
- parameter perturbation;
- PSR/DSR ou Reality Check quando houver muitas variantes correlacionadas.

Critério para avancar:

- vantagem liquida sob custos realistas;
- nao depender de periodo unico;
- nao colapsar em simulacao de execucao realista;
- nao apresentar risco de cauda incompatível;
- benchmark simples continua superado.

### Nivel 5 - Portfolio/Regime Integration

Objetivo: testar se a hipotese melhora o sistema completo.

Testar:

- combinacao com estrategias sobreviventes;
- correlacao;
- contribuicao marginal;
- reducao de drawdown;
- melhora de Sharpe/Calmar;
- comportamento por regime;
- conflito com estrategias existentes;
- turnover e custo agregado.

Critério para avancar:

- melhora marginal clara;
- nao aumenta risco de cauda de forma inaceitavel;
- nao duplica exposicao ja existente;
- tem funcao clara no portfolio;
- nao aumenta complexidade operacional sem recompensa.

### Nivel 6 - Candidate for ADR

Objetivo: preparar decisao formal.

Requisitos:

- resumo da hipotese;
- evidencia quantitativa;
- falhas conhecidas;
- riscos;
- limites;
- condicoes de uso;
- dependencias tecnicas;
- recomendacao: rejeitar, manter em pesquisa, producao experimental ou exigir ADR.

Nivel 6 nao aprova producao sozinho. Qualquer mudanca de risco, sizing, execucao, portfolio allocation, leverage, manifest ou estrategia em producao exige ADR separado.

## 5. Regras de expansao

Um no so pode gerar filhos se atender criterios minimos.

Expandir se:

- passou no nivel atual;
- tem mecanismo causal plausivel;
- resultado liquido e positivo;
- trade_count e suficiente;
- drawdown esta controlado;
- robustez minima foi observada;
- o proximo teste tem custo justificado;
- ainda nao ha no equivalente testado;
- a mutacao proposta responde a uma pergunta concreta.

Nao expandir se:

- resultado depende de poucos trades;
- PnL vem de evento isolado;
- slippage destrói o edge;
- pequena mudanca parametrica colapsa o resultado;
- mecanismo causal e fraco;
- ja ha no equivalente testado;
- risco de data snooping e alto;
- filho proposto e apenas grid search.

Limites de filhos:

- No inicial: maximo 3 filhos.
- No `PROMISING`: maximo 5 filhos.
- No `SURVIVOR`: maximo 8 filhos.

Expansoes acima desses limites exigem ADR metodologico, nao apenas vontade de testar mais.

## 6. Regras de corte precoce

Mover para `GRAVEYARD` se:

- expectancy liquida negativa;
- profit factor abaixo do minimo;
- trade_count insuficiente e sem caminho obvio de correcao;
- drawdown desproporcional;
- resultado colapsa com custos realistas;
- resultado colapsa com pequena perturbacao;
- hipotese nao tem mecanismo causal defensavel;
- duplicacao de hipotese ja rejeitada;
- overfit evidente;
- viola causalidade, lookahead ou fill semantics.

Mover para `QUARANTINED` se:

- resultado e promissor, mas trade_count baixo;
- resultado depende de uma janela suspeita;
- metrica principal e boa, mas risco de cauda e alto;
- precisa de dados adicionais;
- precisa de engine nova;
- precisa de validacao estatistica mais cara;
- resultado contradiz precedentes e exige auditoria.

Mover para `PAUSED` se:

- hipotese e boa, mas custo atual e alto;
- depende de outra etapa;
- depende de dados ainda nao ingeridos;
- depende de implementacao futura;
- depende de ADR antes de qualquer teste significativo.

`REJECTED` e estado transitorio para falha local. Apos registrar causa e regra de nao repeticao em `GRAVEYARD.md`, o status final deve virar `GRAVEYARD`.

## 7. Retorno a melhor bifurcacao

Backtracking e obrigatorio quando o galho atual falha ou quando seu score cai abaixo de alternativas abertas.

Processo:

1. Registrar causa da falha.
2. Mover o no para `GRAVEYARD`, `QUARANTINED` ou `PAUSED`.
3. Subir para o `parent_id`.
4. Verificar irmaos ainda vivos.
5. Escolher o irmao com maior `priority_score`.
6. Se nao houver irmao vivo, subir mais um nivel.
7. Se a familia inteira estiver fraca, retornar a melhor bifurcacao global em `SEARCH_STATE.md`.

A IA deve manter sempre:

- `best_open_nodes`;
- `best_paused_nodes`;
- `best_survivors`;
- `best_quarantined`;
- `rejected_recently`;
- `next_node_to_test`.

Backtracking nao e derrota metodologica. E a principal defesa contra insistencia em hipotese ruim.

## 8. Score de priorizacao

Score inicial:

```text
priority_score =
  0.25 * edge_quality
+ 0.20 * robustness_score
+ 0.15 * causal_plausibility
+ 0.15 * portfolio_value
+ 0.10 * novelty
+ 0.10 * validation_need
- 0.15 * overfit_risk
- 0.10 * compute_cost
- 0.10 * implementation_complexity
```

Cada componente vai de 0 a 10.

O score nao e probabilidade, nao e verdade estatistica e nao substitui julgamento. Ele e uma disciplina operacional para impedir que a IA escolha o proximo teste por curiosidade, recencia ou apego a um galho.

Definicoes:

| Componente | Definicao |
|---|---|
| edge_quality | Qualidade do resultado liquido: expectancy, PF, retorno liquido, Sharpe/Sortino e drawdown. |
| robustness_score | Estabilidade entre janelas, ativos, regimes, perturbacoes e custos. |
| causal_plausibility | Forca do mecanismo causal antes e depois dos resultados. |
| portfolio_value | Utilidade marginal para o sistema: descorrelacao, reducao de DD, funcao por regime. |
| novelty | Diferenca real em relacao a hipoteses ja testadas. |
| validation_need | Importancia estrategica de validar/refutar essa familia. |
| overfit_risk | Risco de mineracao estatistica, single-window, poucos trades ou muitos filhos. |
| compute_cost | Custo estimado do proximo teste. |
| implementation_complexity | Necessidade de codigo novo, dados novos, pipeline novo ou ADR. |

Interpretacao inicial:

- `score >= 6.5`: candidato forte para proximo teste.
- `5.0 <= score < 6.5`: testar se diversifica familia ou valida tese importante.
- `3.5 <= score < 5.0`: manter aberto ou quarentena.
- `score < 3.5`: pausar ou enterrar, salvo dependencia estrategica clara.

## 9. Orcamento progressivo

Unidade de compute e uma abstracao operacional. Pode ser uma run barata, um lote pequeno ou um conjunto minimo definido por ADR de fase.

Orcamento por nivel:

| Nivel | Orcamento maximo por no | Uso |
|---|---:|---|
| Nivel 0 | 0 unidades | Documentacao apenas. |
| Nivel 1 | 1 unidade | Scout barato. |
| Nivel 2 | ate 3 unidades | Replicacao limitada. |
| Nivel 3 | ate 5 unidades | Sensitivity local. |
| Nivel 4 | ate 10 unidades | Robustez e falsificacao. |
| Nivel 5 | ate 15 unidades | Portfolio/regime integration. |
| Nivel 6 | 0 unidades | Documentacao decisoria. |

Regras de alocacao:

- 60% do compute vai para nos `PROMISING` ou `EXPAND`.
- 20% vai para exploracao de novas raizes.
- 10% vai para validacao/falsificacao de sobreviventes.
- 10% vai para quarentena promissora.
- Nunca gastar mais de 10% do orcamento total em uma familia antes de provar robustez fora da amostra.
- Nenhum no pode pular do nivel 1 para o nivel 4 sem nivel 2 ou justificativa documentada.

## 10. Exploracao vs exploracao profunda

Politica padrao:

- 70% exploitation: aprofundar melhores nos.
- 20% exploration: novas familias promissoras.
- 10% falsification: tentar destruir sobreviventes.

O protocolo evita dois erros:

- ganancia miope: abandonar cedo demais uma hipotese com mecanismo forte e scout ruidoso;
- obsessao: insistir em hipotese ruim porque houve um resultado bonito em uma janela.

Regra pratica: uma hipotese com mecanismo forte e resultado ambiguuo pode ir para `QUARANTINED`; uma hipotese com mecanismo fraco e resultado bonito deve ir para validacao barata ou `QUARANTINED`, nunca diretamente para robustez cara.

## 11. Arquivos auxiliares

Este documento recomenda os arquivos auxiliares abaixo. Eles nao sao criados por este protocolo neste momento; seus templates ficam aqui para uso futuro.

### HYPOTHESIS_TREE.md

Funcao: conter a arvore viva.

Deve listar:

- raizes;
- nos filhos;
- `parent_id`;
- status;
- nivel de validacao;
- score;
- proximo passo.

Template:

```markdown
# HYPOTHESIS_TREE

**Updated:** YYYY-MM-DD

## Roots

| node_id | root_family | hypothesis | status | validation_level | priority_score | next_step |
|---|---|---|---|---:|---:|---|
| RM-ROOT-001 | Regime Meta Gating | ... | CANDIDATE | 0 | 6.8 | Scout |

## Tree

### RM-ROOT-001 - short name

| node_id | parent_id | mutation_from_parent | status | level | score | decision | next_children |
|---|---|---|---|---:|---:|---|---|
| RM-001-A | RM-ROOT-001 | Scout ETH 1h 2025H1 | SCOUTING | 1 | 6.8 | pending | RM-001-B, RM-001-C |
```

### NODE_LOG.md

Funcao: diario append-only.

Cada execucao deve registrar:

- `node_id`;
- timestamp;
- acao;
- resultado;
- decisao;
- motivo;
- arquivos afetados;
- proximo no.

Template:

```markdown
# NODE_LOG

## YYYY-MM-DD HH:MM - NODE_ID

- action:
- validation_level:
- result:
- key_metrics:
- decision:
- decision_reason:
- files_affected:
- next_node:
- notes:
```

### SURVIVORS.md

Funcao: listar hipoteses que sobreviveram.

Cada survivor deve ter:

- evidencia resumida;
- nivel atingido;
- limitacoes;
- proximos testes necessarios;
- risco restante.

Template:

```markdown
# SURVIVORS

| node_id | family | level_reached | evidence_summary | limitations | next_tests | remaining_risk |
|---|---|---:|---|---|---|---|
| NODE_ID | Family | 4 | ... | ... | ... | ... |
```

### GRAVEYARD.md

Funcao: listar hipoteses mortas e impedir repeticao.

Obrigatorio registrar:

- causa da morte;
- nivel em que morreu;
- metrica que falhou;
- por que nao repetir;
- excecao que permitiria reabrir.

Template:

```markdown
# GRAVEYARD

| node_id | family | died_at_level | cause_of_death | failed_metric | do_not_repeat_reason | reopen_exception |
|---|---|---:|---|---|---|---|
| NODE_ID | Family | 1 | Expectancy negativa liquida | expectancy | Mecanismo testado e falhou com custos | Reabrir so com dados/codigo novo |
```

### EXPANSION_RULES.md

Funcao: regras de geracao de filhos.

Deve impedir:

- variacoes parametricas infinitas;
- duplicacao;
- expansao sem hipotese;
- expansao por PnL isolado.

Template:

```markdown
# EXPANSION_RULES

## Limits

- Candidate max children: 3
- Promising max children: 5
- Survivor max children: 8

## Allowed Mutations

| mutation_type | allowed_when | max_count | notes |
|---|---|---:|---|
| asset_replication | Level 1 pass | 2 | Prefer BTC/ETH/SOL |
| window_replication | Level 1 pass | 2 | Adjacent era or OOS |
| parameter_sensitivity | Level 2 pass | 4 | +/-10%, +/-20% only |

## Blocked Mutations

- Pure grid without causal reason.
- Duplicate of rejected node.
- New child after Graveyard decision.
```

### VALIDATION_LADDER.md

Funcao: detalhar os niveis 0 a 6.

Template:

```markdown
# VALIDATION_LADDER

| level | name | objective | max_compute | entry_requirement | pass_requirement | fail_action |
|---:|---|---|---:|---|---|---|
| 0 | Idea Node | Register before test | 0 | Hypothesis + mechanism | Complete node | No backtest |
| 1 | Scout Test | Cheap signal detection | 1 | Level 0 complete | Positive liquid expectancy | Graveyard/Quarantine |
| 2 | Replication Test | Check locality | 3 | Level 1 pass | Edge direction preserved | Cut/Quarantine |
| 3 | Sensitivity Test | Local robustness | 5 | Level 2 pass | No param collapse | Cut |
| 4 | Robustness Test | Statistical resistance | 10 | Level 3 pass | Survives stress/OOS | Survivor/Cut |
| 5 | Portfolio Integration | System value | 15 | Level 4 pass | Improves portfolio | Candidate/Reject |
| 6 | Candidate for ADR | Decision package | 0 | Evidence complete | ADR-ready summary | ADR/research/reject |
```

### SEARCH_STATE.md

Funcao: estado operacional atual.

Deve conter:

- `current_node`;
- `current_branch`;
- `best_open_nodes`;
- `best_survivors`;
- `best_quarantined`;
- `recently_rejected`;
- `compute_budget_used`;
- `compute_budget_remaining`;
- `next_action`;
- `last_decision`;
- `blocked_items`.

Template:

```yaml
current_node:
current_branch:
best_open_nodes:
  - node_id:
    priority_score:
    reason:
best_survivors:
  - node_id:
    level:
    reason:
best_quarantined:
  - node_id:
    reason:
recently_rejected:
  - node_id:
    reason:
compute_budget_used:
compute_budget_remaining:
next_action:
last_decision:
blocked_items:
  - item:
    reason:
updated_at:
```

## 12. Formato de decisao apos cada teste

Apos cada teste, a IA deve emitir decisao padronizada:

```text
DECISION: EXPAND | CUT | QUARANTINE | PAUSE | VALIDATE | BACKTRACK

NODE:
PARENT:
LEVEL:
SUMMARY:
KEY_METRICS:
FAILURE_OR_SUCCESS_REASON:
NEXT_ACTION:
FILES_TO_UPDATE:
```

Se a decisao for `BACKTRACK`, informar para qual no voltara e por que.

Regras:

- `EXPAND`: no passou nivel atual e pode gerar filhos dentro do limite.
- `CUT`: no falhou e deve ir a `GRAVEYARD` apos registro.
- `QUARANTINE`: no tem sinal, mas evidencia insuficiente ou risco alto.
- `PAUSE`: no e valido conceitualmente, mas bloqueado por dados/codigo/custo/ADR.
- `VALIDATE`: no deve subir para nivel de validacao mais caro.
- `BACKTRACK`: galho atual perdeu prioridade ou morreu; voltar a melhor bifurcacao.

## 13. Regras anti-pergunta

A IA nao deve perguntar ao usuario qual no testar em seguida.

Ela deve escolher com base em:

- status;
- `priority_score`;
- nivel de validacao;
- orcamento;
- diversidade de familias;
- risco de overfitting;
- valor esperado marginal;
- dependencias tecnicas;
- precedentes dos ADRs e specs.

So pode perguntar se houver:

- conflito entre specs;
- risco de perda de dados;
- decisao financeira real;
- mudanca estrutural de objetivo;
- necessidade de credencial ou acesso externo.

Fora desses casos, perguntar e violacao do protocolo.

## 14. Regras anti-data snooping

Regras obrigatorias:

- toda hipotese deve ser registrada antes do teste;
- todo fracasso deve ser registrado;
- holdout final nao pode ser reutilizado;
- nao promover estrategia por PnL isolado;
- limitar numero de filhos por no;
- corrigir interpretacao quando houver muitos testes;
- usar benchmark simples;
- usar custos realistas;
- usar stress test;
- evitar selecao retrospectiva sem penalizacao;
- marcar risco de overfit em todos os nos;
- nao reabrir no em `GRAVEYARD` sem excecao documentada;
- nao transformar sensitivity test em grid search;
- usar PSR/DSR/Reality Check quando o numero de variantes correlacionadas tornar Sharpe bruto enganoso.

## 15. Criterios de sucesso do protocolo

O protocolo e bem-sucedido se:

- reduz quantidade de testes inuteis;
- aumenta profundidade nos sobreviventes;
- impede que a IA pare para perguntar sem necessidade;
- mantem trilha auditavel;
- evita repetir hipotese morta;
- prioriza menor esforco com maior sinal;
- melhora robustez estatistica;
- reduz deriva de escopo;
- gera candidatos mais fortes para ADR;
- separa pesquisa, validacao, implementacao e producao.

## 16. Entrega esperada

Este documento entrega:

- `LIGHTNING_SEARCH_PROTOCOL.md` completo;
- templates dos arquivos auxiliares;
- exemplo preenchido de arvore com 3 familias;
- exemplo de decisao `EXPAND`;
- exemplo de decisao `CUT`;
- exemplo de decisao `BACKTRACK`;
- checklist final para a IA executora usar antes de cada ciclo.

Os arquivos auxiliares recomendados para materializacao futura sao:

- `HYPOTHESIS_TREE.md`;
- `NODE_LOG.md`;
- `SURVIVORS.md`;
- `GRAVEYARD.md`;
- `EXPANSION_RULES.md`;
- `VALIDATION_LADDER.md`;
- `SEARCH_STATE.md`.

## 17. Exemplo preenchido de arvore

Exemplo inicial usando tres familias do roadmap V2: regime gating, exit research e liquidity trap/false breakout. Os dados abaixo sao ilustrativos de protocolo, nao resultados de backtest.

### Raizes

| node_id | parent_id | root_family | tier | status | validation_level | hypothesis | priority_score | next_step |
|---|---|---|---|---|---:|---|---:|---|
| RM-ROOT-001 | null | Regime Meta Gating | T3 | CANDIDATE | 0 | BTC risk-off gate protege alt longs | 7.0 | Scout ETH/SOL 1h em uma janela |
| EX-ROOT-001 | null | Exit Research | T2 | CANDIDATE | 0 | Time stop curto melhora MR | 6.8 | Scout em BB/RSI 1h |
| LQ-ROOT-001 | null | Liquidity Trap | T1 | CANDIDATE | 0 | Falso rompimento da maxima/minima anterior reverte | 7.2 | Scout 1h OHLCV |

### Regime gating branch

```yaml
node_id: RM-001-A
parent_id: RM-ROOT-001
root_family: Regime Meta Gating
tier: T3
status: CANDIDATE
hypothesis: BTC risk-off gate reduz drawdown de alt longs sem destruir retorno liquido.
causal_mechanism: BTC em queda domina beta de ETH/SOL; bloquear alt longs nesse estado reduz perdas sistemicas.
mutation_from_parent: Scout inicial em ETH 1h com gate BTC return 24h < 0.
asset: ETH
timeframe: 1h
direction: long
entry_logic: long entries canonicas do stack ou candidato V2 aplicavel
exit_logic: sinal base congelado
filters: BTC return 24h < 0 veto
sizing: fixed_notional baseline
data_window: uma janela discovery preregistrada
validation_level: 1
compute_cost_estimate: 1
result_summary: pending
metrics:
  net_return:
  max_drawdown:
  sharpe:
  sortino:
  calmar:
  profit_factor:
  expectancy:
  win_rate:
  payoff_ratio:
  trade_count:
  exposure:
  turnover:
  fees:
  slippage:
  worst_loss_streak:
  stability_by_window:
  stability_by_asset:
  stability_by_regime:
overfit_risk: medium
decision: pending
decision_reason: pending
next_children:
  - RM-001-B replicate SOL 1h
  - RM-001-C replicate adjacent window
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
```

### Exit research branch

```yaml
node_id: EX-001-A
parent_id: EX-ROOT-001
root_family: Exit Research
tier: T2
status: CANDIDATE
hypothesis: Time stop de 6 barras melhora MR ao cortar trades que nao revertem cedo.
causal_mechanism: Em mean reversion 1h, demora excessiva para reverter indica drift adverso ou regime errado.
mutation_from_parent: Scout em uma entry MR canonica, mantendo entry congelada e alterando apenas exit.
asset: SOL
timeframe: 1h
direction: bi
entry_logic: BB/RSI canonical MR
exit_logic: time stop 6 bars ou signal exit, o que ocorrer primeiro
filters: width canonical se a entry original exigir
sizing: fixed_notional baseline
data_window: uma janela discovery preregistrada
validation_level: 1
compute_cost_estimate: 1
result_summary: pending
metrics:
  net_return:
  max_drawdown:
  sharpe:
  sortino:
  calmar:
  profit_factor:
  expectancy:
  win_rate:
  payoff_ratio:
  trade_count:
  exposure:
  turnover:
  fees:
  slippage:
  worst_loss_streak:
  stability_by_window:
  stability_by_asset:
  stability_by_regime:
overfit_risk: medium
decision: pending
decision_reason: pending
next_children:
  - EX-001-B time stop 12 bars sensitivity
  - EX-001-C replicate BTC/ETH
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
```

### Liquidity trap branch

```yaml
node_id: LQ-001-A
parent_id: LQ-ROOT-001
root_family: Liquidity Trap
tier: T1
status: CANDIDATE
hypothesis: Falso rompimento da maxima anterior seguido de close dentro do range gera reversao short.
causal_mechanism: Stops acima de maxima visivel viram liquidez; se o mercado rejeita o rompimento, compradores tardios ficam presos.
mutation_from_parent: Scout OHLCV 1h usando maxima anterior e close back inside range.
asset: BTC
timeframe: 1h
direction: short
entry_logic: break previous high then close back below previous high
exit_logic: VWAP/mean proxy ou time stop curto
filters: wick rejection confirmation
sizing: fixed_notional baseline
data_window: uma janela discovery preregistrada
validation_level: 1
compute_cost_estimate: 1
result_summary: pending
metrics:
  net_return:
  max_drawdown:
  sharpe:
  sortino:
  calmar:
  profit_factor:
  expectancy:
  win_rate:
  payoff_ratio:
  trade_count:
  exposure:
  turnover:
  fees:
  slippage:
  worst_loss_streak:
  stability_by_window:
  stability_by_asset:
  stability_by_regime:
overfit_risk: medium-high
decision: pending
decision_reason: pending
next_children:
  - LQ-001-B long version false break of low
  - LQ-001-C add volume confirmation
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
```

## 18. Exemplos de decisao

Os exemplos abaixo sao modelos de texto. Os numeros sao placeholders ilustrativos e nao resultados reais.

### Exemplo EXPAND

```text
DECISION: EXPAND

NODE: EX-001-A
PARENT: EX-ROOT-001
LEVEL: 1
SUMMARY: Scout do time stop curto em MR 1h apresentou melhora liquida vs signal exit baseline, com trade_count suficiente e reducao de drawdown.
KEY_METRICS:
  net_return: placeholder
  max_drawdown: placeholder
  profit_factor: placeholder
  expectancy: positive after fees/slippage
  trade_count: >= 30
FAILURE_OR_SUCCESS_REASON: A hipotese causal segue plausivel: trades MR que nao revertem cedo tiveram pior MAE e menor payoff. Resultado nao dependeu de 1 ou 2 trades extremos.
NEXT_ACTION: Criar ate 3 filhos: replicacao em outro ativo, replicacao em outra janela e sensitivity time stop 12 bars.
FILES_TO_UPDATE:
  - HYPOTHESIS_TREE.md
  - NODE_LOG.md
  - SEARCH_STATE.md
```

### Exemplo CUT

```text
DECISION: CUT

NODE: LQ-001-A
PARENT: LQ-ROOT-001
LEVEL: 1
SUMMARY: Scout de falso rompimento da maxima anterior falhou com custos realistas.
KEY_METRICS:
  net_return: negative after fees/slippage
  profit_factor: below minimum
  expectancy: negative
  trade_count: sufficient
FAILURE_OR_SUCCESS_REASON: O mecanismo de sweep nao apareceu no proxy OHLCV usado. Slippage e fees consumiram os poucos reversals; pequenas mudancas no criterio de wick pioraram o resultado.
NEXT_ACTION: Mover LQ-001-A para GRAVEYARD. Nao repetir falso rompimento short com esse proxy sem dado adicional de volume/order book ou uma nova definicao causal preregistrada.
FILES_TO_UPDATE:
  - HYPOTHESIS_TREE.md
  - NODE_LOG.md
  - GRAVEYARD.md
  - SEARCH_STATE.md
```

### Exemplo BACKTRACK

```text
DECISION: BACKTRACK

NODE: RM-001-C
PARENT: RM-001-A
LEVEL: 2
SUMMARY: Replicacao em janela adjacente colapsou; o gate BTC risk-off melhorou apenas a janela discovery.
KEY_METRICS:
  stability_by_window: failed
  expectancy: not preserved
  max_drawdown: not improved
FAILURE_OR_SUCCESS_REASON: A hipotese ainda pode ter valor, mas o galho atual nao justifica robustez cara. Risco de single-window selection alto.
NEXT_ACTION: Marcar RM-001-C como QUARANTINED e voltar para EX-001-A, que tem maior priority_score entre best_open_nodes e menor implementation_complexity.
FILES_TO_UPDATE:
  - HYPOTHESIS_TREE.md
  - NODE_LOG.md
  - SEARCH_STATE.md
```

## 19. Checklist antes de cada ciclo

Antes de qualquer ciclo de pesquisa, a IA executora deve confirmar:

- O no existe no `HYPOTHESIS_TREE.md`.
- O no tem `parent_id` ou e raiz explicita.
- A hipotese esta registrada antes do teste.
- O mecanismo causal esta escrito.
- O criterio de sucesso esta escrito.
- O criterio de invalidacao esta escrito.
- O nivel de validacao atual esta definido.
- O compute estimado esta dentro do orcamento do nivel.
- O no nao duplica item em `GRAVEYARD.md`.
- O holdout final nao sera usado indevidamente.
- Custos, fees e slippage realistas estao incluidos.
- O teste e pequeno o suficiente para o nivel atual.
- A proxima mutacao nao e grid search disfarçado.
- O resultado sera registrado mesmo se falhar.
- A decisao final usara o formato padronizado.
- Se falhar, havera backtracking para melhor bifurcacao.
- Nenhuma regra de risco, estrategia existente ou producao sera alterada.
- Qualquer necessidade de codigo novo, dados adicionais, validacao estatistica ou ADR esta marcada.

## 20. Revisao final obrigatoria

Checklist de conformidade deste protocolo:

| Item | Status | Evidencia no documento |
|---|---|---|
| Evita roadmap linear | OK | Seções 1, 7, 10 |
| Usa arvore real com parent_id | OK | Seções 3, 17 |
| Tem regra de expansao | OK | Seção 5 |
| Tem regra de corte | OK | Seção 6 |
| Tem backtracking | OK | Seção 7 e exemplo BACKTRACK |
| Tem orcamento progressivo | OK | Seção 9 |
| Tem score de priorizacao | OK | Seção 8 |
| Tem controle contra overfitting | OK | Seções 4, 8, 14 |
| Tem registro de mortos | OK | Seções 6, 11 |
| Tem autonomia operacional | OK | Seção 13 |
| Impede perguntas desnecessarias | OK | Seção 13 |
| Separa pesquisa de implementacao | OK | Escopo inicial, seções 4 e 6 |
| Nao altera codigo | OK | Escopo inicial |
| Nao promete resultado nao testado | OK | Seções 16, 17, 18 |

Se qualquer item acima enfraquecer em uso futuro, corrigir o protocolo antes de continuar a busca.
