# ROADMAP_ESTRATEGIAS_V2_METODOLOGICO

**Data:** 2026-04-25  
**Status:** proposta metodologica, nao executada  
**Escopo:** pesquisa e desenho de testes; nao altera codigo, nao roda backtest, nao aprova producao.

## 1. Objetivo do roadmap V2

O roadmap V2 substitui a logica de "1000 probes" por uma agenda menor, preregistrada e orientada por hipoteses estruturais. O objetivo nao e gerar volume de backtests, mas descobrir se existe edge robusto, causalmente plausivel, liquido, executavel e resistente a validacao fora da amostra.

A unidade de pesquisa deixa de ser a variacao isolada de parametro e passa a ser a hipotese falsificavel. Cada hipotese precisa declarar mecanismo causal esperado, limite de variacoes, criterio de sucesso, criterio de invalidacao, custos, slippage, dados necessarios, risco de overfitting e dependencia futura.

Este documento tambem serve como roteiro operacional para uma IA executora trabalhar por semanas sem pedir decisoes intermediarias. Se houver ambiguidade, a regra e consultar ADRs, roadmaps anteriores, manifests aprovados, specs e precedentes do projeto; adotar uma hipotese conservadora; registrar a assuncao; continuar.

## Assuncoes adotadas

- O projeto ativo e o diretorio `teste`, pois contem `.git`, `STATE.md`, ADRs recentes, `decisions/roadmap_1000.md`, `exports/HANDOFF_ESTRATEGIAS.md` e artefatos do roadmap antigo.
- O roadmap atual de referencia e `decisions/roadmap_1000.md`, descrito em ADR-0203 e expandido por ADR-0209/0210.
- O stack canonico atual permanece intocado. O handoff indica 13 combos e runtime `faithful`; propostas de exits, sizing ou portfolio sao pesquisa futura, nao regra de producao.
- `fixed_notional_literal` segue como baseline de comparacao. Qualquer sizing dinamico requer ADR antes de producao.
- Testes com funding, order book, spread historico, depth, liquidations ou latency real exigem dados adicionais.
- O roadmap V2 nao declara que qualquer estrategia funciona. Todos os itens abaixo comecam em status `preregistrada V2, nao testada`.

## 2. Critica metodologica do roadmap atual

O roadmap antigo tem valor operacional: organiza 1000 entradas por tier, engine, direcao, timeframe, ativo, janela, filtro, parametros, prior e rationale; possui preregistro por ADR; registra vencedoras; usa gates minimos de Sharpe/trades; e ja reconhece OOS, custos e stress. A estrutura e auditavel e gerou aprendizados reais, como Padrao 43, Padrao 46, Padrao 50 e a fragilidade de snowball/governor em MR.

O problema e que a maior parte do volume ainda nasce de produto cartesiano entre engine, ativo, timeframe, janela e parametros. Isso aumenta data snooping, cria falsa sensacao de cobertura e tende a promover outliers locais. O roadmap tambem tem pouco foco em exits alternativos, sizing como parte da estrategia, portfolio construction, liquidez/microestrutura e falsificacao estatistica formal.

Classificacao dos blocos atuais:

| Bloco atual | Acao V2 | Motivo |
|---|---|---|
| Preregistro por ADR, gates, closeouts e registro de fracassos | manter | Boa disciplina metodologica e rastreabilidade. |
| Validacao OOS, walk-forward, Monte Carlo e cost stress existentes | manter e fortalecer | Infra essencial, mas precisa de holdout final e estatisticas contra data snooping. |
| Stack canonico 13 e manifests aprovados | manter como baseline | Serve de controle e comparacao, nao deve ser reotimizado sem ADR. |
| Regime meta do Tier 1 antigo | transformar em familia menor | Ideia forte, mas antigo espalha filtros por ativo/janela sem mecanismo de promocao claro. |
| Portfolio stack13 | transformar em familia menor | Importante, mas precisa medir correlacao, drawdown conjunto, turnover e capacidade. |
| Param grids BB/RSI/composite | reduzir | Ja ha muita evidencia de sensibilidade; novas variacoes so como perturbacao local. |
| Timeframes 5m/10m/15m/30m em MR | mover para backlog | Padrao 46 indica ruido/custos; voltar so com mecanismo novo de microestrutura. |
| Keltner, zscore, supertrend, Donchian reaberturas amplas | mover para backlog | Historico de refutacao ou outlier unico; exigir gatilho causal novo. |
| LINK/DOT/AVAX grids amplos | mover para backlog | Requer triagem de liquidez/regime antes de compute. |
| Exotic/ML/funding/orderbook do Tier 4 antigo | manter no backlog controlado | Nao devem competir por compute sem dados e protocolo estatistico. |
| Parametros exoticos sem novidade de hipotese | descartar por baixa novidade | Mudam numeros, nao mecanismo. |
| AND/OR de filtros ja refutados isoladamente | descartar ou exigir ablation forte | Padrao 17: composicao herda a perna fraca. |

Blocos fortes:

- Registro de decisoes por ADR e pre-reg por fase.
- Separacao entre manifests aprovados, staging, closeout e refutacao.
- Reconhecimento de custos, slippage, spread stress e causalidade anti-lookahead.
- Meta-analises de correlacao e Padrao 43 como criterio anti-redundancia.
- Aprendizado explicito de padroes negativos, como Padrao 41, 45, 46 e 48.

Blocos redundantes ou com risco de curve fitting:

- Sweeps de parametros em Bollinger/RSI quando a hipotese e apenas "talvez outro numero funcione".
- Repeticao de engine family em mesmo asset/filtro/direcao sem tese de diversificacao.
- Testes single-window que parecem fortes apenas em ETH 2025-H1 ou SOL 2024-H2.
- Reaberturas de engines ja refutadas sem mecanismo novo.
- Asset expansion sem triagem previa de liquidez, volatilidade, spread e regime.

Hipoteses ausentes:

- Exit research sistematico.
- Sizing como componente testavel, com drawdown e cauda como metricas primarias.
- Regime detection separado de estrategia.
- Portfolio construction com cap de correlacao e alocacao por drawdown.
- Liquidity traps, false breakout, sweep, wick rejection e exhaustion.
- Stress de execucao realista: spread variavel, missing candles, latency, capacidade e fill assumptions.
- Controle formal contra data snooping: Deflated Sharpe, Probabilistic Sharpe e Reality Check quando aplicavel.

## 3. Nova filosofia de teste

O V2 opera com menos testes e mais densidade metodologica:

- Menos variantes parametricas, mais hipoteses causais.
- Menos grid search, mais sensitivity local de candidatos ja plausiveis.
- Mais invalidacao explicita e menos narrativa pos-resultado.
- Mais exits, sizing, regime detection e portfolio construction.
- Mais falsificacao: custos, slippage, spread, missing candles, latency, cross-era e cross-asset.
- Mais comparacao contra benchmark simples: buy-and-hold ajustado, flat, fixed notional, equal weight e stack canonico.
- Menos complexidade operacional: familia so avanca se melhorar robustez, nao apenas PnL.

Regra central: resultado forte precisa sobreviver a OOS, custos, slippage, liquidez, perturbacao de parametros, trades suficientes, estabilidade por janela, estabilidade por ativo e mecanismo causal plausivel.

## 4. Sistema de classificacao das hipoteses

Cada hipotese deve ser preregistrada com os campos abaixo antes de rodar:

| Campo | Regra |
|---|---|
| ID | Prefixo da familia + numero sequencial. |
| Nome | Frase curta que identifique o teste. |
| Familia | Uma das familias V2: Regime, Exit, Sizing, Portfolio, Liquidity, Robustness, Exploratory. |
| Hipotese | Declaracao falsificavel. |
| Mecanismo causal esperado | Por que o edge deveria existir antes de ver resultado. |
| Ativos | BTC, ETH, SOL por default; alts so com triagem. |
| Timeframes | 1h default; 4h e 10m apenas quando mecanismo justificar. |
| Direcao | long, short, bi ou adaptive. |
| Entradas | Engine/sinal base ou evento estrutural. |
| Saidas | Exit de referencia ou exit pesquisado. |
| Filtros | Regime/meta-gate permitido; limite de combinacoes por familia. |
| Sizing | Baseline fixed notional ou sizing pesquisado. |
| Custos/slippage | Baseline + stress; nenhum resultado bruto promove. |
| Dados necessarios | OHLCV, funding, spread, order book, trades, latency, manifests. |
| Criterio de sucesso | Metricas minimas, robustez e comparacao contra benchmark. |
| Criterio de invalidacao | Condicoes que encerram a hipotese sem novas variacoes. |
| Risco de overfitting | Baixo, medio, alto; alto exige validacao estatistica mais forte. |
| Prioridade | P0, P1, P2 ou P3. |
| Status | Default: `preregistrada V2, nao testada`. |

Limite de variacoes por familia: no maximo 3 thresholds principais, 3 ativos, 3 janelas e 2 timeframes, salvo ADR explicito. Parametros entram como sensitivity tests, nao como caca aleatoria.

## 5. Tiers do roadmap V2

| Tier | Nome | Objetivo | Regras de entrada | Regras de saida |
|---|---|---|---|---|
| T1 | Hipoteses estruturais de alto valor esperado | Testar mecanismos com causalidade forte e impacto potencial no stack. | Hipotese clara, engine ou dados disponiveis, benchmark definido, criterio de invalidacao. | Promove para validacao dedicada se passar OOS inicial e stress; rejeita se falhar mecanismo ou robustez. |
| T2 | Exits e gestao de posicao | Verificar se o edge atual e limitado por saida ruim, MFE/MAE ou cauda. | Entry baseline fixa e exit isolado como variavel. | Mantem apenas exits que melhoram retorno ajustado sem reduzir trades a amostra pequena. |
| T3 | Regime detection e meta-filtros | Separar quando operar de como operar. | Filtro causalmente plausivel e testavel sem lookahead. | Promove se melhora estabilidade cross-era e reduz drawdown sem destruir trade count. |
| T4 | Portfolio construction e combinacao | Reduzir risco conjunto e redundancia do stack. | Series de retornos alinhadas, custos e turnover disponiveis. | Promove se melhora Calmar/drawdown conjunto vs equal weight e stack atual. |
| T5 | Robustness, falsificacao e stress tests | Tentar quebrar candidatos antes de producao. | Candidato ja observado/promissor. | Valida se sobrevive a holdout, perturbacao, custos, slippage e estatistica; rejeita se fragil. |
| T6 | Backlog exploratorio controlado | Guardar ideias sem consumir compute agora. | Mecanismo incompleto, dados ausentes ou codigo novo pesado. | Reabre so com ADR, dados prontos e criterio de falsificacao. |

## 6. Roadmap de hipoteses

O V2 contem 180 hipoteses/testes. A distribuicao e propositalmente menor que 1000 e aproximadamente igual ao alvo solicitado:

| Familia | Qtde | Percentual | Observacao |
|---|---:|---:|---|
| Regime/meta-filtros | 36 | 20.0% | Inclui volatilidade, HTF, volume, funding e risk-on/risk-off. |
| Exits | 36 | 20.0% | Corrige a lacuna mais clara do roadmap antigo. |
| Position sizing | 27 | 15.0% | Pesquisa futura; nao altera regras de risco atuais. |
| Portfolio construction | 27 | 15.0% | Foco em correlacao, drawdown e rotacao. |
| Liquidity traps / false breakout / sweep / exhaustion | 27 | 15.0% | Principal fronteira causal nova. |
| Sensitivity robusta / falsificacao | 18 | 10.0% | Nao e grid; e tentativa de quebrar candidatos. |
| Ideias exploratorias | 9 | 5.0% | Controladas por dados/codigo/ADR. |

Nao ha desvio percentual relevante. O total foi escolhido para permitir execucao em ciclos com preregistro, OOS e closeout sem repetir a inflacao do roadmap antigo.

## 7. Familias obrigatorias a incluir

### A. Regime Meta Gating

Objetivo: testar se o edge depende de estados de mercado detectaveis antes do trade. Gatilhos obrigatorios: expansao/contracao de volatilidade, tendencia HTF, inclinacao de media movel, largura Bollinger/Keltner, realized volatility percentile, volume relativo, funding extremo quando houver dados e regime risk-on/risk-off entre BTC, ETH e SOL.

Regra: regime gate nao pode ser otimizado no mesmo holdout da estrategia. Primeiro valida-se o regime como classificador de ambiente; depois aplica-se ao entry.

### B. Exit Research

Objetivo: descobrir se os winners atuais sao limitados por exits por sinal bruto. Testar time stop, ATR trailing stop, Chandelier, partial take profit, break-even after MFE, adverse excursion exit, volatility contraction exit, perda de momentum, reversao HTF, compressao/expansao de banda e take profit adaptativo por regime.

Regra: entry fica congelada. Se entry e exit mudarem juntos, o teste e invalido para conclusao sobre exit.

### C. Position Sizing

Objetivo: tratar sizing como parte da estrategia, mas sem promover sizing dinamico por PnL bruto. Testar fixed fractional, volatility targeting, risk parity por ativo, anti-martingale, snowball controlado, Kelly fracionado apenas como benchmark, reducao apos drawdown, aumento apenas apos edge confirmado, sizing por regime e sizing por qualidade do sinal.

Regra: qualquer sizing dinamico aprovado em pesquisa ainda requer ADR antes de producao. Kelly nao e regra de producao direta.

### D. Liquidity Trap / False Breakout

Objetivo: buscar mecanismos onde participantes previsiveis sao forcados a sair: falso rompimento de maxima/minima anterior, sweep de liquidez, wick rejection, stop hunt em regioes obvias, breakout com falha de continuacao, reversao apos expansao extrema, exaustao com volume anormal e retorno para VWAP/media apos spike.

Regra: sem order book, usar OHLCV como proxy conservadora. Com order book, registrar dados adicionais e stress de capacidade.

### E. Portfolio Stack

Objetivo: melhorar o stack por combinacao e alocacao, nao por reotimizacao de cada estrategia. Testar equal weight, risk parity volatility, min variance, correlation cap, drawdown-aware allocation, regime-based allocation, strategy rotation, ensemble voting, ensemble com veto por regime e separacao por ativo/timeframe.

Regra: comparar sempre contra stack atual, equal weight e fixed notional.

### F. Robustness & Falsification

Objetivo: tentar refutar os sobreviventes. Testes obrigatorios: walk-forward, OOS, cross-asset, cross-era, Monte Carlo trade shuffle, fee/slippage stress, spread stress, missing candle stress, latency stress, parameter perturbation, data snooping control, Deflated Sharpe Ratio, Probabilistic Sharpe Ratio e White's Reality Check quando aplicavel.

Regra: se uma hipotese so vence no discovery set, ela nao vence.

## 8. Controle contra data snooping

- Separar `discovery set`, `validation set` e `final holdout`.
- O final holdout nao pode ser reutilizado para ajustar parametro, filtro, ativo, timeframe, direction ou sizing.
- Cada familia tem limite explicito de variantes. Atingido o limite, parar e fechar ADR.
- Registrar hipoteses antes do teste, incluindo criterio de invalidacao.
- Registrar todos os fracassos, inclusive runs com erro, baixa liquidez ou poucos trades.
- Nao promover estrategia apenas por PnL.
- Exigir metricas de robustez: estabilidade por janela, ativo, regime, custo e perturbacao.
- Exigir benchmark simples: buy-and-hold ajustado, flat, equal weight, fixed notional ou stack canonico.
- Repetir teste apenas se houver bug documentado, dado corrigido ou ADR de reabertura.
- Quando houver muitas variantes correlacionadas, aplicar PSR/DSR e Reality Check antes de declarar edge.

## 9. Metricas obrigatorias

Todo teste deve registrar:

- retorno liquido;
- max drawdown;
- Sharpe;
- Sortino;
- Calmar;
- profit factor;
- win rate;
- payoff ratio;
- expectancy;
- numero de trades;
- exposicao;
- turnover;
- fees;
- slippage;
- pior sequencia de perdas;
- estabilidade por janela;
- estabilidade por ativo;
- estabilidade por regime.

Metricas adicionais recomendadas: MAE, MFE, tail loss p95/p99, tempo medio em posicao, capacidade estimada, correlacao com stack, contribution to portfolio drawdown, turnover por asset e degradacao sob spread.

## 10. Criterios de promocao

| Nivel | Criterios minimos |
|---|---|
| Rejeitada | Falha criterio de invalidacao, trade count insuficiente, sem mecanismo plausivel ou colapso com custo/slippage realista. |
| Observada | Sinal aparece no discovery set, com trades suficientes, mas ainda sem validacao independente. |
| Promissora | Passa discovery e validation, melhora benchmark simples e nao depende de um unico trade/janela. |
| Candidata | Passa OOS inicial, cost stress, perturbacao local e estabilidade minima por ativo ou regime. |
| Validada | Passa walk-forward, final holdout, Monte Carlo, fee/slippage/spread stress, e tem DSR/PSR aceitavel quando aplicavel. |
| Producao experimental | Validada, operacionalmente simples, monitoravel, com limites de risco e rollback definidos por ADR. |
| Producao proibida ate ADR | Qualquer item que altere sizing, risco, execution semantics, leverage, portfolio allocation ou dependencias de dados novos. |

## 11. Criterios de descarte rapido

Uma hipotese deve ser descartada se:

- so funciona em um unico ativo e uma unica janela;
- depende de poucos trades;
- colapsa com slippage realista;
- colapsa com pequena alteracao parametrica;
- tem drawdown incompativel;
- so melhora PnL as custas de cauda absurda;
- nao tem mecanismo causal plausivel;
- vence apenas por overfitting evidente;
- melhora Sharpe removendo trades ate perder poder estatistico;
- exige dado que nao estaria disponivel causalmente no momento de decisao;
- piora turnover/custos sem melhorar retorno liquido ajustado.

## 12. Plano de execucao

| Fase | Objetivo | Hipoteses | Max testes | Dependencias | Criterios de parada | Outputs esperados |
|---|---|---:|---:|---|---|---|
| Fase 1 | Auditoria do roadmap antigo | Critica + classificacao | 0 backtests | roadmaps, ADRs, STATE, winners | Documento V2 aprovado como plano | Sumario de manter/reduzir/backlog/descartar |
| Fase 2 | Selecao T1 | RM001-RM012, LQ001-LQ009 | 21 | engine existente e OHLCV | 2 familias sem sinal robusto encerram bloco | ADR prereg + shortlist estrutural |
| Fase 3 | Exit research | EX001-EX036 | 36 | entries baseline congeladas | Exit que reduz trade count demais ou piora stress e descartado | Ranking de exits por familia/asset |
| Fase 4 | Regime gating | RM013-RM036 | 24 | filtros existentes + dados adicionais quando marcados | Gate sem lift OOS ou com lookahead risco alto e encerrado | Metagates candidatos |
| Fase 5 | Position sizing | PS001-PS027 | 27 | series de trades, risco atual | Drawdown/cauda piora sem retorno ajustado | Sizing report, sem producao |
| Fase 6 | Portfolio stack | PF001-PF027 | 27 | returns alinhados, custos, correlacao | Nao supera equal weight/stack atual | Alocacoes candidatas e rejeitadas |
| Fase 7 | Liquidity traps | LQ010-LQ027 | 18 | OHLCV; orderbook se usado | Proxies sem robustez cross-asset param | Familia microestrutura curta |
| Fase 8 | Robustness/falsification | RB001-RB018 | 18 | candidatos das fases 2-7 | Qualquer candidato que falha holdout final e rebaixado | Relatorio de sobreviventes |
| Fase 9 | Consolidacao | Sobreviventes | ate 20 reruns | resultados completos | Sem sobrevivente com robustez suficiente | Lista final: validada, candidata, rejeitada |
| Fase 10 | Preparacao futura | Itens candidatos a implementacao | 0 backtests | ADRs necessarios | Nenhuma mudanca sem ADR | Backlog tecnico e ADRs propostos |

## 13. Backlog controlado

| Item | Motivo para nao entrar agora | Condicao de reabertura |
|---|---|---|
| 5m MR amplo | Padrao 46 indica ruido/custos em intra-hour; baixo valor esperado. | Somente com microestrutura e spread real. |
| 10m MR adicional | Frente 10m ja exaurida em engines disponiveis. | Novo mecanismo causal, nao novo parametro. |
| Keltner/zscore novos grids | Historico de refutacao cross-window. | Evidencia de regime especifico detectavel antes do trade. |
| Supertrend/MA trend-following amplo | Padrao 50 e single-regime ETH 2025-H1. | Regime detector de bear alt validado fora da amostra. |
| LINK/DOT/AVAX grids extensos | Asset expansion anterior sem promocao. | Triagem previa de liquidez, spread, volatilidade e regime. |
| ML classifiers | Alto risco de data snooping e necessidade de pipeline separado. | Dataset versionado, feature store causal e protocolo DSR/Reality Check. |
| Order book imbalance | Requer dados adicionais, storage e simulacao de latencia. | Dados historicos de depth/trades e modelo de execucao. |
| Funding arbitrage | Funding nao esta garantido no dataset atual. | Serie de funding causal por exchange e custo de carregar posicao. |
| Martingale/grid agressivo | Conflita com controle de cauda e regras de risco. | Nao reabrir sem decisao financeira real e ADR de risco. |
| Kelly em producao | Sensivel a erro de estimativa; risco de ruina. | Apenas benchmark academico; producao proibida ate ADR. |

## 14. Formato de tabela final

Legenda de dependencia:

- `engine existente`: pode ser pesquisado com engines/filtros/scripts atuais ou pequenas composicoes de artefatos.
- `novo codigo`: exige implementacao futura.
- `dados adicionais`: exige fonte de dados ainda nao garantida.
- `validacao estatistica`: exige PSR/DSR/Reality Check, bootstrap ou protocolo especifico.
- `ADR antes de producao`: pode ser pesquisado, mas nao pode ir para producao sem decisao formal.

Todas as hipoteses abaixo tem status inicial: `preregistrada V2, nao testada`.

| ID | Tier | Familia | Hipotese | Mecanismo causal | Engine | Dir | TF | Asset | Entry | Exit | Filter | Sizing | Window/Data | Validacao | Prioridade | Risco Overfit | Requer codigo? | Criterio de sucesso | Criterio de invalidacao |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RM001 | T3 | Regime Meta Gating | Gate por expansao ATR melhora stack MR | MR sofre em ruido baixo e ganha em volatilidade negociavel | regime_meta | adaptive | 1h | BTC/ETH/SOL | stack 13 | sinal base | ATR pct >= p70 | fixed notional | 2024H2-2025H2 OHLCV | OOS + cost stress | P0 | medio | engine existente | Calmar e Sharpe sobem vs stack sem gate | Lift so em uma janela ou trades < 30 |
| RM002 | T3 | Regime Meta Gating | Gate por contracao ATR evita whipsaw em trend-follow | Trend-follow precisa evitar regime lateral estreito | regime_meta | adaptive | 10m/1h | ETH/SOL | MA/ST candidatos | sinal base | ATR pct <= p30 bloqueia | fixed notional | 2024H2-2025H2 OHLCV | cross-era | P1 | medio | engine existente | Reduz MDD sem perder alfa em bear alt | Bloqueia winners e nao reduz DD |
| RM003 | T3 | Regime Meta Gating | HTF trend 4h positivo melhora longs MR/BB | Tendencia maior reduz risco de mean reversion contra queda estrutural | bollinger/rsi | long | 1h | BTC/ETH/SOL | entries canonicas | sinal base | close > SMA50 4h | fixed notional | OHLCV 4h causal | walk-forward | P0 | medio | engine existente | Sortino e drawdown melhoram em 2+ ativos | Piora retorno liquido ou gera lookahead |
| RM004 | T3 | Regime Meta Gating | HTF trend 4h negativo melhora shorts | Shorts de reversao ganham em ambiente de distribuicao | bollinger/rsi | short | 1h | BTC/ETH/SOL | entries canonicas short | sinal base | close < SMA50 4h | fixed notional | OHLCV 4h causal | OOS | P0 | medio | engine existente | Sharpe liquido melhora vs width-only | Falha em 2 de 3 ativos |
| RM005 | T3 | Regime Meta Gating | Slope SMA 1h filtra regimes directionais | Inclinacao captura drift sem depender de nivel absoluto | regime_meta | adaptive | 1h | BTC/ETH/SOL | stack 13 | sinal base | slope SMA50 tercis | fixed notional | OHLCV | WF + perturbacao | P1 | medio | engine existente | Estabilidade por regime melhora | Sensivel ao periodo 30/50/80 |
| RM006 | T3 | Regime Meta Gating | Bollinger width p70 melhora short mean reversion | Bandas largas indicam excesso exploravel e paga custos | bollinger/rsi | short | 1h | BTC/ETH/SOL | canonical short | sinal base | BB width >= p70 | fixed notional | OHLCV | OOS + cost | P0 | baixo | engine existente | Melhora PF e expectancy vs min_bps fixo | Threshold vizinho colapsa |
| RM007 | T3 | Regime Meta Gating | Bollinger width p30 bloqueia trades em compressao | Compressao reduz amplitude para pagar fees | bollinger/rsi | bi | 1h | BTC/ETH/SOL | canonical MR | sinal base | BB width <= p30 veto | fixed notional | OHLCV | cross-window | P1 | medio | engine existente | Fees/turnover caem e Sharpe sobe | Reducao de trades explica todo lift |
| RM008 | T3 | Regime Meta Gating | Keltner width confirma volatilidade estrutural | ATR band width e menos sensivel a outliers que sigma | regime_meta | adaptive | 1h | BTC/ETH/SOL | stack 13 | sinal base | Keltner width tercis | fixed notional | OHLCV | OOS | P2 | medio | novo codigo | Lift replica BB width sem sobreajuste | Redundante e pior que BB width |
| RM009 | T3 | Regime Meta Gating | Realized volatility percentile separa MR de trend | Vol realizada define se reversao tem amplitude suficiente | regime_meta | adaptive | 1h | BTC/ETH/SOL | stack 13 | sinal base | RV p20/p80 | fixed notional | OHLCV | WF | P0 | medio | novo codigo | Regime melhora estabilidade por janela | RV so seleciona janela vencedora |
| RM010 | T3 | Regime Meta Gating | Volume relativo alto valida breakout | Continuidade exige participacao acima do normal | ma_crossover/supertrend | long/bi | 10m/1h | ETH/SOL | trend entries | sinal base | rel volume >= 1.5 | fixed notional | OHLCV volume | cross-era | P1 | alto | novo codigo | P50 melhora fora de ETH 2025H1 | Funciona so no regime conhecido |
| RM011 | T3 | Regime Meta Gating | Volume relativo extremo invalida MR entry | Volume anormal pode indicar repricing, nao excesso reversivel | bollinger/rsi | bi | 1h | BTC/ETH/SOL | MR extremes | sinal base | veto rel vol >= 3 | fixed notional | OHLCV volume | OOS | P1 | medio | novo codigo | Reduz perdas de cauda sem matar PF | Remove winners e reduz expectancy |
| RM012 | T3 | Regime Meta Gating | Funding extremo melhora contrarian short/long | Funding extremo sinaliza crowding e risco de squeeze/reversal | regime_meta | adaptive | 1h/4h | BTC/ETH/SOL | MR/liq entries | adaptive | funding zscore | fixed notional | funding + OHLCV | holdout final | P2 | alto | dados adicionais | Edge liquido sobrevive por exchange | Sem dados causalmente disponiveis |
| RM013 | T3 | Regime Meta Gating | BTC risk-off gate protege alt longs | BTC em queda domina beta de ETH/SOL | regime_meta | long | 1h | ETH/SOL | long entries | sinal base | BTC return 24h < 0 veto | fixed notional | multi-asset OHLCV | OOS | P0 | baixo | engine existente | MDD alt cai sem perda grande de retorno | Alpha vira apenas beta timing |
| RM014 | T3 | Regime Meta Gating | ETH/BTC relative strength gate melhora ETH longs | Lideranca relativa indica fluxo especifico | regime_meta | long | 1h | ETH | long entries | sinal base | ETH/BTC slope > 0 | fixed notional | BTC/ETH OHLCV | cross-era | P1 | medio | novo codigo | Lift em ETH sem overtrading | Falha cross-era |
| RM015 | T3 | Regime Meta Gating | SOL/BTC relative weakness melhora SOL shorts | Fraqueza relativa aumenta continuacao para shorts | regime_meta | short | 1h | SOL | short entries | sinal base | SOL/BTC slope < 0 | fixed notional | BTC/SOL OHLCV | OOS | P1 | medio | novo codigo | Shorts SOL melhoram PF e DD | So seleciona bear unico |
| RM016 | T3 | Regime Meta Gating | Risk-on tri-asset permite maior exposicao MR long | Correlacao positiva e drift alto reduzem risco de reversao incompleta | regime_meta | long | 1h | BTC/ETH/SOL | MR long | sinal base | BTC/ETH/SOL above SMA | fixed notional | multi-asset OHLCV | WF | P2 | medio | novo codigo | Calmar portfolio melhora | Aumenta correlacao e drawdown |
| RM017 | T3 | Regime Meta Gating | Risk-off tri-asset ativa bear-avoidance trend | Trend-follow longo pode perder menos que B&H em bear alt | ma_crossover/supertrend | long/bi | 10m/1h | ETH/SOL | MA/ST | signal/ATR exit | tri-asset risk-off | fixed notional | OHLCV | final holdout | P0 | alto | novo codigo | P50 replica em ativo/janela nova | Continua preso a ETH 2025H1 |
| RM018 | T3 | Regime Meta Gating | Regime de chop favorece BB/RSI width | MR precisa de reversoes dentro de range | regime_meta | bi | 1h | BTC/ETH/SOL | BB/RSI | sinal base | ADX baixo + width medio | fixed notional | OHLCV | OOS | P0 | medio | novo codigo | Stack MR melhora vs width-only | ADX nao adiciona valor |
| RM019 | T3 | Regime Meta Gating | Regime de tendencia bloqueia MR contra drift | Mean reversion perde quando drift domina | regime_meta | bi | 1h | BTC/ETH/SOL | MR entries | sinal base | ADX alto veto contra tendencia | fixed notional | OHLCV | WF | P1 | medio | novo codigo | MDD cai e Sortino melhora | Reduz retorno sem reduzir cauda |
| RM020 | T3 | Regime Meta Gating | Vol-of-vol alta exige menor exposicao | Mudancas bruscas de vol aumentam erro de stop/exit | regime_meta | adaptive | 1h | BTC/ETH/SOL | stack 13 | sinal base | vol-of-vol p80 | scaled down | OHLCV | cost + OOS | P2 | medio | novo codigo + ADR antes de producao | Cauda p95 melhora | Menor retorno explica tudo |
| RM021 | T3 | Regime Meta Gating | Range compression antes de breakout melhora trend entries | Compressao acumula energia direcional | ma_crossover/supertrend | long/bi | 1h | BTC/ETH/SOL | breakout/trend | ATR trail | BB/KC squeeze | fixed notional | OHLCV | OOS | P1 | alto | novo codigo | Breakouts superam baseline trend | Falha com slippage/spread |
| RM022 | T3 | Regime Meta Gating | Expansao pos-compressao invalida MR inicial | Primeiro movimento pos-squeeze tende a continuar | bollinger/rsi | bi | 1h | BTC/ETH/SOL | MR extremes | time stop | squeeze release veto | fixed notional | OHLCV | cross-era | P1 | medio | novo codigo | Reduz losers grandes de MR | Reduz winners e PF |
| RM023 | T3 | Regime Meta Gating | Janela horario UTC influencia slippage/edge | Liquidez e volatilidade variam por sessao | regime_meta | adaptive | 1h | BTC/ETH/SOL | stack 13 | sinal base | session buckets | fixed notional | OHLCV + volume | OOS | P2 | medio | novo codigo | Sessao melhora net apos custos | Apenas seleciona pouca amostra |
| RM024 | T3 | Regime Meta Gating | Fim de semana exige filtro separado | Liquidez menor e gaps mudam comportamento crypto | regime_meta | adaptive | 1h | BTC/ETH/SOL | stack 13 | sinal base | weekend/weekday | fixed notional | OHLCV | OOS | P2 | baixo | novo codigo | Weekend filter reduz slippage proxy | Sem diferenca estatistica |
| RM025 | T3 | Regime Meta Gating | Correlacao rolling alta reduz trades simultaneos | Exposicoes correlacionadas elevam DD conjunto | regime_meta | adaptive | 1h | BTC/ETH/SOL | stack entries | sinal base | corr cap | fixed notional | returns aligned | portfolio OOS | P0 | medio | novo codigo | Portfolio MDD cai sem perder Sharpe | Retorno cai proporcionalmente |
| RM026 | T3 | Regime Meta Gating | Regime de drawdown do proprio stack reduz risco | Drawdown recente pode indicar regime adverso | regime_meta | adaptive | 1h | multi | stack 13 | sinal base | stack DD state | reduced notional | equity curve | WF | P2 | alto | novo codigo + ADR antes de producao | Calmar melhora robustamente | Governor repete Padrao 48 kill |
| RM027 | T3 | Regime Meta Gating | Realized beta a BTC define alocacao alt | Beta alto transforma alts em exposicao duplicada | regime_meta | adaptive | 1h | ETH/SOL | stack alt | sinal base | beta rolling | fixed/reduced | multi-asset OHLCV | OOS | P1 | medio | novo codigo | DD portfolio cai | Reduz diversificacao real |
| RM028 | T3 | Regime Meta Gating | Break de regime por retorno 7d extremo bloqueia MR | Movimento forte de varios dias e repricing persistente | regime_meta | bi | 1h | BTC/ETH/SOL | MR entries | sinal base | abs ret 7d p90 | fixed notional | OHLCV | cross-era | P1 | medio | engine existente | Evita cauda sem perder expectancy | Veto depende de threshold fragil |
| RM029 | T3 | Regime Meta Gating | Skew de candle recente antecipa reversao | Sequencia de wicks assimetricos indica absorcao | regime_meta | adaptive | 1h | BTC/ETH/SOL | MR/liq entries | sinal base | wick skew | fixed notional | OHLCV | OOS | P2 | alto | novo codigo | Melhora entries de sweep | Nao replica em ativos |
| RM030 | T3 | Regime Meta Gating | Volatilidade normalizada por horario reduz falso edge | Horarios de alta vol nao devem ser confundidos com regime | regime_meta | adaptive | 1h | BTC/ETH/SOL | stack 13 | sinal base | RV percentile por sessao | fixed notional | OHLCV | holdout | P3 | alto | novo codigo | Lift persiste apos normalizar sessao | Lift desaparece |
| RM031 | T3 | Regime Meta Gating | Regime de baixa liquidez aumenta custo efetivo | Spread e slippage podem consumir edge aparente | regime_meta | adaptive | 1h | BTC/ETH/SOL | stack 13 | sinal base | volume low veto | fixed notional | OHLCV volume | cost stress | P0 | medio | novo codigo | Net melhora sob spread stress | Sem efeito apos custos |
| RM032 | T3 | Regime Meta Gating | Volatilidade relativa ETH vs BTC guia rotacao | ETH edge depende de vol idiossincratica | regime_meta | adaptive | 1h | ETH | ETH entries | sinal base | RV_ETH/RV_BTC | fixed notional | multi OHLCV | OOS | P2 | alto | novo codigo | ETH melhora sem overfit | Threshold fragil |
| RM033 | T3 | Regime Meta Gating | SOL idiosyncratic volatility favorece MR | SOL MR ganha quando move por fluxo proprio, nao beta BTC | regime_meta | bi | 1h | SOL | SOL MR | sinal base | residual vol SOL | fixed notional | multi OHLCV | OOS | P1 | alto | novo codigo | Replica Padrao 48 fora da janela | Apenas reidentifica SOL 2024H2 |
| RM034 | T3 | Regime Meta Gating | Gate de drawdown de B&H ativa bear-avoidance | Trend-following longo pode ser hedge em drawdown profundo | ma_crossover/supertrend | long/bi | 10m/1h | ETH/SOL | trend entries | signal/ATR | B&H DD > 35% | fixed notional | OHLCV | final holdout | P0 | alto | novo codigo | Passa em bear novo, nao bull | So funciona por saber fundo ex-post |
| RM035 | T3 | Regime Meta Gating | Combinar regime com veto simples supera AND complexo | Um gate causal forte deve vencer composicoes frageis | regime_meta | adaptive | 1h | BTC/ETH/SOL | stack 13 | sinal base | best single gate vs AND | fixed notional | OHLCV | ablation | P1 | medio | engine existente | Single gate iguala ou supera AND | AND tem lift robusto |
| RM036 | T3 | Regime Meta Gating | Meta-gate por qualidade de sinal reduz trades ruins | Distancia ao threshold mede conviccao do sinal | regime_meta | adaptive | 1h | BTC/ETH/SOL | BB/RSI entries | sinal base | signal strength tercis | fixed notional | OHLCV | OOS | P1 | alto | novo codigo | Top tercil melhora expectancy sem amostra pequena | Top tercil so reduz N |
| EX001 | T2 | Exit Research | Time stop curto melhora MR | MR que nao reverte rapido tende a virar drift adverso | exit_layer | bi | 1h | BTC/ETH/SOL | BB/RSI canonical | exit apos 6 bars | width canonical | fixed notional | trades baseline | OOS | P0 | medio | novo codigo | MAE e DD caem com Sharpe maior | Lucro cai por cortar winners |
| EX002 | T2 | Exit Research | Time stop medio captura reversao completa | Reversao 1h pode precisar de 12-24 candles | exit_layer | bi | 1h | BTC/ETH/SOL | BB/RSI canonical | exit apos 18 bars | width canonical | fixed notional | trades baseline | WF | P1 | medio | novo codigo | Calmar melhora vs signal exit | Sensivel a 12/18/24 |
| EX003 | T2 | Exit Research | Time stop longo evita capital preso | Posicoes longas aumentam exposicao sem edge | exit_layer | bi | 1h | BTC/ETH/SOL | stack entries | exit apos 48 bars | canonical | fixed notional | trades baseline | OOS | P2 | baixo | novo codigo | Exposicao cai sem reduzir net | Trade count ou PnL colapsa |
| EX004 | T2 | Exit Research | ATR trailing stop reduz cauda | Stop dinamico segue volatilidade e limita tendencia adversa | exit_layer | bi | 1h | BTC/ETH/SOL | MR entries | ATR trail 2.5x | width | fixed notional | OHLCV | cost + OOS | P0 | medio | novo codigo | MDD cai e Sortino sobe | Stop gera whipsaw custoso |
| EX005 | T2 | Exit Research | ATR trailing largo preserva winners | MR pode precisar de espaco contra ruido | exit_layer | bi | 1h | BTC/ETH/SOL | MR entries | ATR trail 4x | width | fixed notional | OHLCV | sensitivity | P1 | medio | novo codigo | Melhor cauda sem reduzir PF | Similar a sem stop |
| EX006 | T2 | Exit Research | Chandelier exit melhora trend-follow | Trend precisa deixar lucro correr e sair por volatilidade | exit_layer | long/bi | 10m/1h | ETH/SOL | MA/ST | Chandelier 3x | risk-off | fixed notional | OHLCV | cross-era | P0 | medio | novo codigo | P50 melhora fora discovery | Continua single-regime |
| EX007 | T2 | Exit Research | Partial TP 50% em 1R reduz variancia | Realiza parte do MFE e deixa cauda positiva | exit_layer | bi | 1h | BTC/ETH/SOL | stack entries | 50% TP + signal | canonical | fixed notional | OHLCV | OOS | P1 | medio | novo codigo | Sortino e DD melhoram | Expectancy cai por truncar winners |
| EX008 | T2 | Exit Research | Partial TP por banda media melhora BB | Alvo natural de MR e retorno a media | bollinger_exit | bi | 1h | BTC/ETH/SOL | BB entry | 50% na media, resto signal | width | fixed notional | OHLCV | OOS | P0 | medio | novo codigo | PF melhora vs exit media total | Sem melhora liquida apos custos |
| EX009 | T2 | Exit Research | Break-even after MFE reduz losers tardios | Depois de lucro relevante, perda cheia e falha de reversao | exit_layer | bi | 1h | BTC/ETH/SOL | stack entries | BE apos MFE 1 ATR | canonical | fixed notional | OHLCV | cost stress | P0 | medio | novo codigo | Reduz pior sequencia sem cortar muito PnL | BE aumenta churn |
| EX010 | T2 | Exit Research | Break-even tardio evita ruido | BE cedo demais pode transformar winners em scratch | exit_layer | bi | 1h | BTC/ETH/SOL | stack entries | BE apos MFE 2 ATR | canonical | fixed notional | OHLCV | sensitivity | P1 | medio | novo codigo | Melhor que BE 1 ATR em PF | Sem diferenca robusta |
| EX011 | T2 | Exit Research | Adverse excursion exit elimina trades quebrados | MAE acima do historico indica hipotese do trade falhou | exit_layer | bi | 1h | BTC/ETH/SOL | MR entries | exit MAE p80 | width | fixed notional | trade path | OOS | P0 | alto | novo codigo | Tail loss p95 cai e Calmar sobe | MAE threshold overfit |
| EX012 | T2 | Exit Research | MFE decay exit protege lucro devolvido | Devolucao grande apos MFE indica reversao abortada | exit_layer | bi | 1h | BTC/ETH/SOL | stack entries | exit se devolve 60% MFE | canonical | fixed notional | trade path | WF | P1 | alto | novo codigo | Payoff ratio melhora | Reduz convexidade positiva |
| EX013 | T2 | Exit Research | Volatility contraction exit fecha posicao sem amplitude | Edge de MR depende de amplitude para continuar pagando risco | exit_layer | bi | 1h | BTC/ETH/SOL | MR entries | exit se width cai p30 | width | fixed notional | OHLCV | OOS | P1 | medio | novo codigo | Exposicao cai com net preservado | Fecha antes do alvo |
| EX014 | T2 | Exit Research | Vol expansion exit reduz risco de repricing | Expansao adversa pode virar trend e nao reversao | exit_layer | bi | 1h | BTC/ETH/SOL | MR entries | exit se RV sobe p90 contra posicao | width | fixed notional | OHLCV | OOS | P1 | medio | novo codigo | DD e tail caem | Confunde volatility com oportunidade |
| EX015 | T2 | Exit Research | Momentum loss exit melhora trend-follow | Trend sem momentum vira chop | exit_layer | long/bi | 10m/1h | ETH/SOL | MA/ST | exit RSI/momentum decai | risk-off | fixed notional | OHLCV | cross-era | P1 | alto | novo codigo | Reduz whipsaw P50 | Funciona so em ETH 2025H1 |
| EX016 | T2 | Exit Research | HTF reversal exit protege longs | Reversao 4h invalida tese 1h/10m | exit_layer | long | 1h | BTC/ETH/SOL | long entries | exit close < SMA50 4h | HTF | fixed notional | OHLCV 4h | OOS | P0 | medio | novo codigo | MDD cai sem matar retorno | Sinal 4h atrasado demais |
| EX017 | T2 | Exit Research | HTF reversal exit protege shorts | Reversao 4h contra short aumenta squeeze risk | exit_layer | short | 1h | BTC/ETH/SOL | short entries | exit close > SMA50 4h | HTF | fixed notional | OHLCV 4h | OOS | P0 | medio | novo codigo | Sortino short melhora | Piora winners |
| EX018 | T2 | Exit Research | Banda compression exit apos entry evita chop | Se banda comprime apos sinal, oportunidade perdeu energia | exit_layer | bi | 1h | BTC/ETH/SOL | BB/RSI | exit width compressao | width | fixed notional | OHLCV | WF | P1 | medio | novo codigo | Reduz tempo medio em posicao | Reduz payoff medio |
| EX019 | T2 | Exit Research | Banda expansion exit apos lucro captura blowoff | Expansao extrema apos MFE e exaustao | exit_layer | bi | 1h | BTC/ETH/SOL | MR entries | exit expansion p95 | width | fixed notional | OHLCV | OOS | P2 | alto | novo codigo | Evita devolucao de MFE | Overfit a outliers |
| EX020 | T2 | Exit Research | Take profit adaptativo por regime chop | Chop tem alvo mais curto que trend | exit_layer | bi | 1h | BTC/ETH/SOL | MR entries | TP menor em chop | regime chop | fixed notional | OHLCV | regime OOS | P1 | alto | novo codigo | Expectancy melhora por regime | Regime classifier instavel |
| EX021 | T2 | Exit Research | Take profit adaptativo por regime trend | Trend permite alvo maior ou trailing | exit_layer | long/short | 1h | BTC/ETH/SOL | trend/MR | TP/trail em trend | ADX/RV | fixed notional | OHLCV | OOS | P1 | alto | novo codigo | Calmar melhora vs TP fixo | Aumenta cauda |
| EX022 | T2 | Exit Research | Exit por VWAP reversion em liquidity spike | Depois do spike, preco tende a voltar ao valor medio | exit_layer | bi | 1h | BTC/ETH/SOL | LQ spike | VWAP/session mean | vol spike | fixed notional | OHLCV/VWAP | OOS | P2 | alto | novo codigo | Spike trades tem PF > baseline | VWAP proxy invalida |
| EX023 | T2 | Exit Research | Exit por close alem do wick extremo invalida rejection | Se o mercado aceita o preco alem do wick, rejeicao falhou | liquidity_exit | bi | 1h | BTC/ETH/SOL | wick rejection | close beyond wick | wick filter | fixed notional | OHLCV | OOS | P0 | medio | novo codigo | Tail loss cai | Stop muito proximo |
| EX024 | T2 | Exit Research | Exit por candle contrario forte apos entry | Candle contrario grande indica absorcao oposta | exit_layer | bi | 1h | BTC/ETH/SOL | stack entries | contra candle > 1.5 ATR | canonical | fixed notional | OHLCV | WF | P2 | alto | novo codigo | Reduz losers persistentes | Mata reversoes normais |
| EX025 | T2 | Exit Research | Exit no proximo sinal oposto com double-cost explicito | Reverse pode ser melhor que flat em regimes alternantes | engine | bi | 1h | BTC/ETH/SOL | bidirectional | reverse on signal | canonical | fixed notional | OHLCV | cost stress | P1 | medio | engine existente | Supera exit-to-flat apos double cost | Custos consomem lift |
| EX026 | T2 | Exit Research | Exit flat antes de reverse reduz double cost | Evitar abrir oposto imediato reduz churn | exit_layer | bi | 1h | BTC/ETH/SOL | bidirectional | flat cooldown 1 bar | canonical | fixed notional | OHLCV | OOS | P2 | medio | novo codigo | Turnover cai com net preservado | Perde reversoes lucrativas |
| EX027 | T2 | Exit Research | Cooldown apos stop reduz clustering de perdas | Sinais logo apos stop pertencem ao mesmo regime adverso | exit_layer | bi | 1h | BTC/ETH/SOL | stack entries | cooldown 3 bars | canonical | fixed notional | trades | OOS | P2 | alto | novo codigo | Pior sequencia cai | Repete governor destrutivo |
| EX028 | T2 | Exit Research | Exit por max holding reduz exposure drag | Menor exposicao reduz risco exogeno | exit_layer | bi | 1h | BTC/ETH/SOL | stack entries | max holding p90 baseline | canonical | fixed notional | trades baseline | WF | P1 | medio | novo codigo | Exposicao cai com Sharpe maior | Parametro p90 overfit |
| EX029 | T2 | Exit Research | Exit por retorno a media parcial em RSI | RSI extremes podem normalizar antes do preco tocar media | rsi_exit | bi | 1h | BTC/ETH/SOL | RSI entry | exit RSI 50 | width | fixed notional | OHLCV | OOS | P1 | medio | novo codigo | Melhor que signal canonical | Sinal fecha cedo demais |
| EX030 | T2 | Exit Research | Exit por slope de media contra posicao | Slope captura drift que invalida reversao | exit_layer | bi | 1h | BTC/ETH/SOL | MR entries | exit slope contra | SMA slope | fixed notional | OHLCV | OOS | P1 | medio | novo codigo | MDD e tail melhoram | Slope redundante ao entry |
| EX031 | T2 | Exit Research | Exit por gap/open adverse reduz perda de execucao | Open seguinte muito adverso sugere repricing | exit_layer | bi | 1h | BTC/ETH/SOL | stack entries | exit on adverse gap | canonical | fixed notional | OHLCV | cost stress | P3 | alto | novo codigo | Slippage stress melhora | Depende de fill impossivel |
| EX032 | T2 | Exit Research | Exit por spread stress proxy evita trades caros | Volume baixo e range alto implicam custo maior | exit_layer | bi | 1h | BTC/ETH/SOL | stack entries | exit if cost proxy high | volume/range | fixed notional | OHLCV volume | stress | P2 | medio | novo codigo | Net melhora em stress spread | Proxy nao prediz custo |
| EX033 | T2 | Exit Research | Exit de cauda por ATR hard stop como benchmark | Mesmo se producao nao usar stop, benchmark mede risco | exit_layer | bi | 1h | BTC/ETH/SOL | stack entries | hard stop 3 ATR | canonical | fixed notional | OHLCV | OOS | P0 | medio | novo codigo | Define tradeoff DD/return | Stop piora tudo |
| EX034 | T2 | Exit Research | Exit por quantil MAE por engine | Cada engine tem assinatura de excursao adversa | exit_layer | bi | 1h | BTC/ETH/SOL | per-engine | MAE p85 engine | canonical | fixed notional | trade paths | WF | P1 | alto | novo codigo | Robustez por engine melhora | Threshold nao transfere |
| EX035 | T2 | Exit Research | Exit por quantil MFE nao realizado | Falha em monetizar MFE indica exit ruim | exit_layer | bi | 1h | BTC/ETH/SOL | stack entries | trail MFE p60 | canonical | fixed notional | trade paths | OOS | P1 | alto | novo codigo | Payoff/expectancy melhora | Trunca outliers bons |
| EX036 | T2 | Exit Research | Exit ensemble simples supera exit unico | Veto de cauda + signal exit pode ser mais robusto | exit_layer | bi | 1h | BTC/ETH/SOL | stack entries | min(signal, tail veto) | canonical | fixed notional | OHLCV | holdout | P2 | alto | novo codigo + ADR antes de producao | Melhora robusta sem complexidade excessiva | Complexidade nao paga |
| PS001 | T2 | Position Sizing | Fixed fractional 0.5% risco por trade como benchmark | Normaliza risco entre ativos e volatilidades | sizing_layer | bi | 1h | BTC/ETH/SOL | stack entries | sinal base | canonical | fixed fractional | trades + ATR | OOS | P1 | medio | novo codigo + ADR antes de producao | Calmar melhora vs fixed notional | Cauda piora ou sizing instavel |
| PS002 | T2 | Position Sizing | Fixed fractional 1.0% mede elasticidade | Sensitivity de risco, nao otimizacao | sizing_layer | bi | 1h | BTC/ETH/SOL | stack entries | sinal base | canonical | fixed fractional | trades + ATR | stress | P2 | medio | novo codigo + ADR antes de producao | Retorno escala sem DD desproporcional | DD cresce mais que retorno |
| PS003 | T2 | Position Sizing | Vol targeting por ativo reduz concentracao em SOL | Vol alta deve receber menor notional | sizing_layer | bi | 1h | BTC/ETH/SOL | stack entries | sinal base | canonical | vol target | OHLCV | portfolio OOS | P0 | medio | novo codigo + ADR antes de producao | MDD portfolio cai | Retorno cai proporcionalmente |
| PS004 | T2 | Position Sizing | Vol targeting por estrategia reduz cauda local | Engines com cauda maior recebem menos capital | sizing_layer | bi | 1h | multi | stack 13 | sinal base | canonical | vol target strategy | returns | OOS | P1 | medio | novo codigo + ADR antes de producao | Calmar melhora vs equal notional | Overfit a janela |
| PS005 | T2 | Position Sizing | Risk parity por ativo melhora diversificacao | Equal risk evita dominancia de ativo volatil | sizing_layer | adaptive | 1h | BTC/ETH/SOL | stack | sinal base | none | risk parity asset | returns | OOS | P0 | medio | novo codigo + ADR antes de producao | DD conjunto menor que fixed | Correlacao alta anula beneficio |
| PS006 | T2 | Position Sizing | Risk parity por combo melhora stack | Combos com risco distinto devem contribuir igualmente | sizing_layer | adaptive | 1h | multi | stack 13 | sinal base | none | risk parity combo | returns | OOS | P1 | medio | novo codigo + ADR antes de producao | Portfolio Sharpe/Calmar sobe | Turnover/alocacao instavel |
| PS007 | T2 | Position Sizing | Anti-martingale leve apos equity high | Aumentar so quando sistema esta confirmando edge | sizing_layer | adaptive | 1h | multi | stack | sinal base | none | +25% at equity high | equity curve | WF | P2 | alto | novo codigo + ADR antes de producao | Retorno sobe sem piorar DD | Vira pro-ciclico destrutivo |
| PS008 | T2 | Position Sizing | Anti-martingale por trade MFE confirmado | Escalar apenas depois de movimento favoravel reduz risco inicial | sizing_layer | bi | 1h | BTC/ETH/SOL | entries | MFE scale | canonical | add after MFE | trade path | OOS | P2 | alto | novo codigo + ADR antes de producao | Payoff melhora sem cauda | Recria pyramid refutado |
| PS009 | T2 | Position Sizing | Snowball controlado capado e benchmark | Medir se snowball com teto evita ADR-0064 | sizing_layer | bi | 1h | multi | stack | sinal base | none | snowball cap 1.25x | equity | stress | P3 | alto | novo codigo + ADR antes de producao | Nao piora Sharpe/DD vs fixed | Qualquer cauda pior invalida |
| PS010 | T2 | Position Sizing | Kelly fracionado 0.25x como benchmark | Mede teto teorico sob incerteza, nao regra produtiva | sizing_layer | adaptive | 1h | multi | stack | sinal base | none | fractional Kelly | trade stats | DSR + stress | P3 | alto | novo codigo + ADR antes de producao | Apenas benchmark informativo | Sensivel a erro de estimativa |
| PS011 | T2 | Position Sizing | Reducao apos drawdown de equity | Diminuir risco quando regime adverso aparece | sizing_layer | adaptive | 1h | multi | stack | sinal base | DD state | half after DD 5% | equity curve | WF | P2 | alto | novo codigo + ADR antes de producao | Tail DD cai sem kill winners | Repete governor Padrao 48 |
| PS012 | T2 | Position Sizing | Reducao apos drawdown por estrategia | Isola problema local sem matar stack | sizing_layer | adaptive | 1h | multi | per combo | sinal base | combo DD | reduce combo | combo equity | OOS | P1 | alto | novo codigo + ADR antes de producao | DD contribution cai | Perde recuperacao MR |
| PS013 | T2 | Position Sizing | Aumento apenas apos edge confirmado OOS | Evita escalar discovery overfit | sizing_layer | adaptive | 1h | multi | validated only | sinal base | status gate | staged size | validation logs | holdout | P0 | baixo | ADR antes de producao | Candidatos escalados preservam metricas | Qualquer candidato regride |
| PS014 | T2 | Position Sizing | Sizing por regime chop/trend | Capital maior onde a engine tem mecanismo | sizing_layer | adaptive | 1h | BTC/ETH/SOL | stack | sinal base | regime classifier | regime size | OHLCV | OOS | P1 | alto | novo codigo + ADR antes de producao | Calmar por regime melhora | Classifier overfit |
| PS015 | T2 | Position Sizing | Sizing por qualidade de sinal BB distance | Distancia maior da banda pode indicar maior edge | sizing_layer | bi | 1h | BTC/ETH/SOL | BB entries | sinal base | signal strength | tercile size | OHLCV | OOS | P1 | alto | novo codigo + ADR antes de producao | Expectancy cresce monotonicamente | Nao ha monotonicidade |
| PS016 | T2 | Position Sizing | Sizing por qualidade de sinal RSI distance | RSI extremo mais profundo pode indicar crowding | sizing_layer | bi | 1h | BTC/ETH/SOL | RSI entries | sinal base | RSI distance | tercile size | OHLCV | OOS | P1 | alto | novo codigo + ADR antes de producao | Expectancy monotonicamente maior | Extremos viram trend loss |
| PS017 | T2 | Position Sizing | Cap de exposicao simultanea por ativo | Evita empilhar riscos correlacionados no mesmo ativo | sizing_layer | adaptive | 1h | BTC/ETH/SOL | stack | sinal base | asset cap | max notional asset | signals | portfolio OOS | P0 | medio | novo codigo + ADR antes de producao | MDD reduz com retorno preservado | Bloqueia melhores trades |
| PS018 | T2 | Position Sizing | Cap de exposicao por direcao | Reduz beta liquido quando varios shorts/longs disparam | sizing_layer | adaptive | 1h | multi | stack | sinal base | direction cap | max long/short | signals | OOS | P1 | medio | novo codigo + ADR antes de producao | Beta/DD menor | Retorno cai sem DD menor |
| PS019 | T2 | Position Sizing | Cap por correlacao rolling | Sinais altamente correlacionados competem por capital | sizing_layer | adaptive | 1h | multi | stack | sinal base | corr cap | allocate best | returns | OOS | P1 | alto | novo codigo + ADR antes de producao | Calmar portfolio sobe | Escolha do best overfit |
| PS020 | T2 | Position Sizing | De-risk em baixa liquidez | Reduz tamanho quando custo esperado sobe | sizing_layer | adaptive | 1h | BTC/ETH/SOL | stack | sinal base | volume/cost proxy | size down | OHLCV volume | cost stress | P1 | medio | novo codigo + ADR antes de producao | Net sob stress melhora | Proxy sem valor |
| PS021 | T2 | Position Sizing | Tamanho fixo por volatilidade alvo diaria | Mantem risco diario estavel | sizing_layer | adaptive | 1h | BTC/ETH/SOL | stack | sinal base | RV daily | daily vol target | OHLCV | WF | P2 | medio | novo codigo + ADR antes de producao | Vol equity mais estavel | Retorno ajustado nao melhora |
| PS022 | T2 | Position Sizing | Stop de tamanho, nao stop de trade | Preserva exit canonico mas controla risco | sizing_layer | adaptive | 1h | multi | stack | sinal base | DD/vol | notional throttle | equity | OOS | P1 | alto | novo codigo + ADR antes de producao | Cauda cai sem Padrao 48 kill | Kill de winners detectado |
| PS023 | T2 | Position Sizing | Rebalance mensal do notional por combo | Atualiza risco devagar para evitar overfit | sizing_layer | adaptive | 1h | multi | stack | sinal base | monthly realized vol | monthly size | returns | OOS | P2 | medio | novo codigo + ADR antes de producao | Menor instabilidade que diario | Sem lift |
| PS024 | T2 | Position Sizing | Rebalance trimestral por robustez | Menor turnover de alocacao | sizing_layer | adaptive | 1h | multi | stack | sinal base | quarterly stats | quarterly size | returns | OOS | P2 | baixo | novo codigo + ADR antes de producao | Calmar melhora com baixa troca | Lento demais para regime |
| PS025 | T2 | Position Sizing | Sizing inverso a turnover esperado | Combos caros recebem menos capital | sizing_layer | adaptive | 1h | multi | stack | sinal base | turnover estimate | cost-aware size | trade stats | cost stress | P1 | medio | novo codigo + ADR antes de producao | Net melhora apos fees | Penaliza edge valido |
| PS026 | T2 | Position Sizing | Sizing por confidence ensemble | Varios sinais concordantes recebem mais peso | sizing_layer | adaptive | 1h | BTC/ETH/SOL | ensemble entries | sinal base | vote count | vote-weight size | signals | OOS | P2 | alto | novo codigo + ADR antes de producao | Expectancy cresce por voto | Votos correlacionados overfit |
| PS027 | T2 | Position Sizing | Baseline fixed_notional 5 niveis como sensitivity | Mede capacidade sem confundir com edge | sizing_layer | bi | 1h | multi | stack | sinal base | none | fixed 1x-5x | trades | stress | P0 | baixo | engine existente | Escala linear liquida ate limite | DD/custo cresce nao-linear |
| PF001 | T4 | Portfolio Stack | Equal weight stack como benchmark formal | Baseline simples evita overclaim de alocacao | portfolio | n/a | 1h | multi | stack 13 returns | n/a | none | equal weight | aligned returns | OOS | P0 | baixo | engine existente | Serve como controle | Nao aplicavel |
| PF002 | T4 | Portfolio Stack | Risk parity volatility melhora MDD | Cada combo contribui risco similar | portfolio | n/a | 1h | multi | stack returns | n/a | none | risk parity vol | returns | OOS | P0 | medio | novo codigo + ADR antes de producao | Calmar > equal weight | Turnover/alocacao instavel |
| PF003 | T4 | Portfolio Stack | Min variance reduz DD conjunto | Otimizacao conservadora reduz exposicao redundante | portfolio | n/a | 1h | multi | stack returns | n/a | none | min variance | returns | holdout | P1 | alto | novo codigo + ADR antes de producao | DD menor sem retorno colapsar | Peso extremo/overfit |
| PF004 | T4 | Portfolio Stack | Correlation cap 0.7 reduz redundancia | Padrao 43 indica pares engine-only redundantes | portfolio | n/a | 1h | multi | stack returns | n/a | corr cap | capped allocation | returns | OOS | P0 | medio | novo codigo + ADR antes de producao | Corr media e DD caem | Remove hedge temporal valido |
| PF005 | T4 | Portfolio Stack | Correlation cap 0.5 testa agressividade | Sensitivity do cap, nao nova busca | portfolio | n/a | 1h | multi | stack returns | n/a | corr cap | capped allocation | returns | sensitivity | P2 | medio | novo codigo + ADR antes de producao | Melhor tradeoff que 0.7 | Retorno cai demais |
| PF006 | T4 | Portfolio Stack | Drawdown-aware allocation reduz capital em combo quebrado | Combo em DD pode estar em regime adverso | portfolio | n/a | 1h | multi | stack returns | n/a | DD state | drawdown-aware | equity curves | WF | P1 | alto | novo codigo + ADR antes de producao | MDD portfolio melhora | Repete governor kill |
| PF007 | T4 | Portfolio Stack | Regime-based allocation MR vs trend | Aloca engines conforme regime causal | portfolio | adaptive | 1h | multi | MR/trend baskets | n/a | regime classifier | regime alloc | OHLCV + returns | OOS | P0 | alto | novo codigo + ADR antes de producao | Supera equal weight por Calmar | Classifier overfit |
| PF008 | T4 | Portfolio Stack | Strategy rotation por trailing Sharpe | Rotacionar para estrategia recente forte | portfolio | adaptive | 1h | multi | stack returns | n/a | trailing stats | top-k | returns | holdout | P3 | alto | novo codigo + ADR antes de producao | DSR aceitavel e Calmar maior | Performance chasing |
| PF009 | T4 | Portfolio Stack | Rotation por regime, nao por PnL | Reduz data snooping de trailing Sharpe | portfolio | adaptive | 1h | multi | baskets | n/a | regime | basket rotation | OHLCV | OOS | P1 | medio | novo codigo + ADR antes de producao | Robustez > PnL rotation | Sem lift vs equal |
| PF010 | T4 | Portfolio Stack | Ensemble voting entry reduz falsos sinais | Concordancia independente pode aumentar precision | ensemble | adaptive | 1h | BTC/ETH/SOL | BB/RSI/Donchian votes | base exit | vote >= 2 | fixed notional | signals | OOS | P2 | alto | novo codigo | Win rate/expectancy sobem | Votos correlacionados e poucos trades |
| PF011 | T4 | Portfolio Stack | Ensemble com veto por regime evita trades ruins | Regime forte pode bloquear sinais correlacionados | ensemble | adaptive | 1h | BTC/ETH/SOL | stack votes | base exit | regime veto | fixed notional | signals+OHLCV | OOS | P1 | alto | novo codigo | Calmar melhora vs voting sem veto | Veto explica por amostra baixa |
| PF012 | T4 | Portfolio Stack | Separacao por ativo reduz beta duplicado | Capital por ativo controla concentracao | portfolio | n/a | 1h | BTC/ETH/SOL | stack returns | n/a | asset buckets | equal per asset | returns | OOS | P0 | medio | novo codigo + ADR antes de producao | DD por ativo controlado | Perde edge do melhor ativo |
| PF013 | T4 | Portfolio Stack | Separacao por timeframe evita overexposure | Timeframes distintos podem diversificar holding periods | portfolio | n/a | 1h/4h/10m | multi | candidates | n/a | tf buckets | equal per TF | returns | OOS | P2 | medio | novo codigo | Corr e DD caem | Timeframes menores refutados |
| PF014 | T4 | Portfolio Stack | Bucket MR vs trend controla regimes | MR e trend tendem a ganhar em ambientes diferentes | portfolio | adaptive | 1h | multi | MR/trend | n/a | basket cap | basket weights | returns | OOS | P1 | medio | novo codigo + ADR antes de producao | Drawdown conjunto menor | Trend basket sem robustez |
| PF015 | T4 | Portfolio Stack | Long/short exposure neutrality reduz beta | Balancear direcao reduz dependencia de mercado | portfolio | adaptive | 1h | multi | stack | n/a | direction exposure | beta-neutral cap | returns | OOS | P1 | alto | novo codigo + ADR antes de producao | Beta/DD menor com retorno | Neutraliza edge direcional |
| PF016 | T4 | Portfolio Stack | Max active trades portfolio reduz crowding | Muitos sinais simultaneos indicam mesmo choque | portfolio | n/a | 1h | multi | stack signals | n/a | max active | priority queue | signals | OOS | P1 | alto | novo codigo + ADR antes de producao | DD reduz sem perder top expectancy | Priority overfit |
| PF017 | T4 | Portfolio Stack | Priority por expectancy OOS, nao discovery | Evita escolher winners locais | portfolio | n/a | 1h | multi | stack signals | n/a | validated rank | priority queue | validation logs | holdout | P0 | medio | novo codigo + ADR antes de producao | Top rank preserva performance | Rank instavel |
| PF018 | T4 | Portfolio Stack | Cap por turnover portfolio reduz custos | Turnover agregado consome edge | portfolio | n/a | 1h | multi | stack | n/a | turnover cap | cost-aware alloc | trades | cost stress | P1 | medio | novo codigo + ADR antes de producao | Net apos fees melhora | Cap bloqueia bons trades |
| PF019 | T4 | Portfolio Stack | Stop de portfolio por volatility spike | Vol extrema aumenta correlacao e slippage | portfolio | n/a | 1h | multi | stack | n/a | portfolio vol p95 | de-risk | returns | stress | P2 | alto | novo codigo + ADR antes de producao | Cauda p99 melhora | Bloqueia recuperacoes |
| PF020 | T4 | Portfolio Stack | Allocation por marginal drawdown contribution | Reduz combos que ampliam DD comum | portfolio | n/a | 1h | multi | stack returns | n/a | MDD contrib | alloc down | returns | OOS | P1 | alto | novo codigo + ADR antes de producao | Portfolio Calmar sobe | Overfit ao DD passado |
| PF021 | T4 | Portfolio Stack | Equal risk per asset-direction bucket | Controla concentracao em short SOL ou long ETH | portfolio | n/a | 1h | multi | stack | n/a | asset-dir buckets | equal risk bucket | returns | OOS | P1 | medio | novo codigo + ADR antes de producao | MDD de bucket cai | Retorno cai sem diversificar |
| PF022 | T4 | Portfolio Stack | Portfolio holdout final sem reotimizacao | Teste de realidade dos sobreviventes | portfolio | n/a | 1h | multi | selected candidates | n/a | frozen | frozen alloc | final holdout | final holdout | P0 | baixo | validacao estatistica | Sobrevive sem ajuste | Qualquer ajuste invalida holdout |
| PF023 | T4 | Portfolio Stack | Ablation one-combo-out mede dependencia | Stack robusto nao depende de um combo | portfolio | n/a | 1h | multi | stack returns | n/a | ablation | equal weight | returns | ablation | P0 | baixo | engine existente | Nenhum combo unico domina | Um combo explica tudo |
| PF024 | T4 | Portfolio Stack | Add-one candidate testa valor marginal | Novo candidato precisa melhorar portfolio, nao isolado | portfolio | n/a | 1h | multi | stack + candidate | n/a | corr + DD | equal/risk | returns | OOS | P0 | medio | engine existente | Melhora Calmar marginal | Alta corr sem lift |
| PF025 | T4 | Portfolio Stack | Cluster por correlacao evita duplicatas | Escolher representante por cluster reduz complexidade | portfolio | n/a | 1h | multi | stack returns | n/a | corr clusters | cluster alloc | returns | OOS | P1 | medio | novo codigo | Complexidade cai sem perda | Remove hedge temporal |
| PF026 | T4 | Portfolio Stack | Portfolio capacity stress por notional | Edge pode degradar com tamanho | portfolio | n/a | 1h | multi | stack | n/a | none | notional ladder | trades/cost | stress | P1 | medio | novo codigo | Capacidade minima definida | Custo nao-linear invalida |
| PF027 | T4 | Portfolio Stack | Paper-trading shadow portfolio | Validar execucao sem capital real | portfolio | n/a | live/paper | multi | selected stack | n/a | live rules | frozen | paper logs | forward test | P0 | baixo | ADR antes de producao | Divergencia backtest/paper aceitavel | Fill/custo diverge materialmente |
| LQ001 | T1 | Liquidity Trap | Falso rompimento da maxima anterior reverte | Stops acima da maxima viram liquidez para reversal | liquidity_trap | short | 1h | BTC/ETH/SOL | break prev high then close below | VWAP/mean | wick rejection | fixed notional | OHLCV | OOS | P0 | medio | novo codigo | PF > MR baseline com custos | Sem replicacao cross-asset |
| LQ002 | T1 | Liquidity Trap | Falso rompimento da minima anterior reverte | Stops abaixo da minima alimentam squeeze | liquidity_trap | long | 1h | BTC/ETH/SOL | break prev low then close above | VWAP/mean | wick rejection | fixed notional | OHLCV | OOS | P0 | medio | novo codigo | Expectancy positiva liquida | Funciona so um ativo/janela |
| LQ003 | T1 | Liquidity Trap | Sweep de high diario com wick alto gera short | Rejeicao de nivel obvio indica absorcao | liquidity_trap | short | 1h | BTC/ETH/SOL | sweep daily high | close to VWAP | wick/volume | fixed notional | OHLCV | cross-era | P0 | medio | novo codigo | Tail controlado e trades >=30 | Wicks nao tem edge |
| LQ004 | T1 | Liquidity Trap | Sweep de low diario com wick baixo gera long | Stop hunt abaixo do low diario pode reverter | liquidity_trap | long | 1h | BTC/ETH/SOL | sweep daily low | close to VWAP | wick/volume | fixed notional | OHLCV | cross-era | P0 | medio | novo codigo | Sharpe liquido > baseline | Colapsa com slippage |
| LQ005 | T1 | Liquidity Trap | Wick rejection > 2 ATR e contrarian | Wick extremo representa tentativa falha de repricing | liquidity_trap | bi | 1h | BTC/ETH/SOL | wick > 2 ATR | time/mean exit | ATR wick | fixed notional | OHLCV | OOS | P1 | medio | novo codigo | MAE controlada e PF >1.2 | Threshold fragil 1.5/2/2.5 |
| LQ006 | T1 | Liquidity Trap | Wick rejection com volume alto e mais forte | Volume confirma participacao e absorcao | liquidity_trap | bi | 1h | BTC/ETH/SOL | wick + rel vol | VWAP/mean | rel vol >=1.5 | fixed notional | OHLCV volume | OOS | P1 | alto | novo codigo | Lift vs wick sem volume | Volume seleciona outliers |
| LQ007 | T1 | Liquidity Trap | Stop hunt em numeros redondos reverte | Niveis psicologicos concentram ordens | liquidity_trap | bi | 1h | BTC/ETH/SOL | sweep round level | mean exit | round level proximity | fixed notional | OHLCV | OOS | P3 | alto | novo codigo | Edge liquido apos custos | Definicao de nivel overfit |
| LQ008 | T1 | Liquidity Trap | Breakout com falha de continuacao vira reversal | Falha apos romper range prende compradores/vendedores | liquidity_trap | bi | 1h | BTC/ETH/SOL | breakout then no follow-through | opposite band/mean | range breakout | fixed notional | OHLCV | OOS | P0 | medio | novo codigo | Reversal supera BB baseline | Poucos trades |
| LQ009 | T1 | Liquidity Trap | Breakout valido exige close longe do range | Fechamento forte indica aceitacao, nao sweep | breakout_filter | long/short | 1h | BTC/ETH/SOL | Donchian/breakout | ATR trail | close extension | fixed notional | OHLCV | cross-era | P1 | medio | novo codigo | Donchian melhora sem overfit | Donchian continua refutado |
| LQ010 | T1 | Liquidity Trap | Reversao apos expansao extrema de range | Movimento muito alem da vol media tende a mean-revert | liquidity_trap | bi | 1h | BTC/ETH/SOL | true range p95 | time/mean exit | RV p95 | fixed notional | OHLCV | OOS | P1 | medio | novo codigo | PF positivo com tail controlada | Continua como trend |
| LQ011 | T1 | Liquidity Trap | Exaustao com volume anormal favorece fade | Climax volume apos extensao indica capitulacao | liquidity_trap | bi | 1h | BTC/ETH/SOL | extension + volume p95 | VWAP/mean | rel volume | fixed notional | OHLCV volume | OOS | P0 | alto | novo codigo | Edge em 2+ ativos | So captura eventos raros |
| LQ012 | T1 | Liquidity Trap | Retorno para VWAP apos spike | VWAP funciona como preco medio de consenso | liquidity_trap | bi | 1h | BTC/ETH/SOL | spike away VWAP | VWAP target | distance zscore | fixed notional | OHLCV/VWAP | OOS | P1 | alto | novo codigo | Expectancy liquida positiva | VWAP proxy ruim |
| LQ013 | T1 | Liquidity Trap | Spike contra HTF trend reverte mais | Movimento contra tendencia maior pode ser stop run | liquidity_trap | bi | 1h | BTC/ETH/SOL | spike contra 4h trend | mean exit | HTF trend | fixed notional | OHLCV 4h | OOS | P1 | alto | novo codigo | Lift vs spike simples | HTF adiciona overfit |
| LQ014 | T1 | Liquidity Trap | Spike a favor HTF trend continua | Movimento com tendencia maior e repricing real | breakout_filter | long/short | 1h | BTC/ETH/SOL | spike with HTF | ATR trail | HTF trend | fixed notional | OHLCV 4h | OOS | P1 | alto | novo codigo | Trend entries melhoram | Falha apos custos |
| LQ015 | T1 | Liquidity Trap | Equal high sweep em range gera short | Maximas iguais concentram stops visiveis | liquidity_trap | short | 1h | BTC/ETH/SOL | equal high sweep | mean/time | range + wick | fixed notional | OHLCV | OOS | P2 | alto | novo codigo | PF >1.2 e N>=30 | Definicao subjetiva |
| LQ016 | T1 | Liquidity Trap | Equal low sweep em range gera long | Minimas iguais concentram stops | liquidity_trap | long | 1h | BTC/ETH/SOL | equal low sweep | mean/time | range + wick | fixed notional | OHLCV | OOS | P2 | alto | novo codigo | PF >1.2 e N>=30 | Definicao subjetiva |
| LQ017 | T1 | Liquidity Trap | Failed retest apos breakout gera continuation oposta | Traders entram no retest e sao expulsos | liquidity_trap | bi | 1h | BTC/ETH/SOL | failed retest | ATR/time | range level | fixed notional | OHLCV | OOS | P2 | alto | novo codigo | Expectancy positiva | Poucos eventos |
| LQ018 | T1 | Liquidity Trap | Opening range sweep UTC gera reversal | Liquidez concentrada no inicio da sessao | liquidity_trap | bi | 1h | BTC/ETH/SOL | sweep first 4h range | VWAP/time | session range | fixed notional | OHLCV | OOS | P2 | alto | novo codigo | Sessao robusta cross-asset | Horario overfit |
| LQ019 | T1 | Liquidity Trap | Liquidation cascade proxy por range+volume reverte | Cascata forcada esgota fluxo temporario | liquidity_trap | bi | 1h | BTC/ETH/SOL | range p99 + volume p99 | mean/time | cascade proxy | fixed notional | OHLCV volume | OOS | P2 | alto | dados adicionais | Edge se mantem com liquidations depois | Proxy falso |
| LQ020 | T1 | Liquidity Trap | Funding extremo + sweep melhora reversal | Crowded perp + stop run cria squeeze | liquidity_trap | bi | 1h/4h | BTC/ETH/SOL | sweep + funding extreme | mean/time | funding | fixed notional | funding + OHLCV | holdout | P2 | alto | dados adicionais | Melhora vs sweep isolado | Funding nao adiciona |
| LQ021 | T1 | Liquidity Trap | Order book imbalance confirma sweep | Absorcao real aparece no livro | liquidity_trap | bi | 1m/1h | BTC/ETH/SOL | sweep + imbalance | VWAP/time | depth imbalance | fixed notional | order book | forward/OOS | P3 | alto | dados adicionais + novo codigo | Edge liquido apos latency | Sem dados/latency invalida |
| LQ022 | T1 | Liquidity Trap | Spread widening invalida entry de trap | Spread alto pode transformar edge bruto em perda | liquidity_trap | bi | 1h | BTC/ETH/SOL | LQ entries | base exit | spread proxy veto | fixed notional | spread/OHLCV | cost stress | P1 | medio | dados adicionais | Net melhora sob stress | Veto sem valor |
| LQ023 | T1 | Liquidity Trap | Sweep duplo sem continuacao aumenta reversao | Duas tentativas falhas indicam absorcao forte | liquidity_trap | bi | 1h | BTC/ETH/SOL | double sweep | mean/time | wick pattern | fixed notional | OHLCV | OOS | P2 | alto | novo codigo | Payoff maior que sweep simples | Poucos trades |
| LQ024 | T1 | Liquidity Trap | Inside bar apos spike sinaliza exaustao | Compressao pos-spike indica fluxo esgotado | liquidity_trap | bi | 1h | BTC/ETH/SOL | spike then inside bar | mean/time | range contraction | fixed notional | OHLCV | OOS | P2 | alto | novo codigo | Win rate melhora | Atraso perde edge |
| LQ025 | T1 | Liquidity Trap | Close back inside range e melhor que wick apenas | Aceitacao dentro do range confirma falha | liquidity_trap | bi | 1h | BTC/ETH/SOL | close inside prior range | mean/time | range | fixed notional | OHLCV | ablation | P0 | medio | novo codigo | Supera wick-only | Sem diferenca |
| LQ026 | T1 | Liquidity Trap | Liquidity trap em 4h e mais robusta que 1h | Niveis 4h tem mais participantes e menos ruido | liquidity_trap | bi | 4h | BTC/ETH/SOL | sweep 4h high/low | mean/time | wick | fixed notional | OHLCV 4h | OOS | P1 | medio | novo codigo | Menor noise e PF maior | Trade count insuficiente |
| LQ027 | T1 | Liquidity Trap | Trap 1h alinhada a nivel 4h aumenta qualidade | Confluencia de niveis concentra liquidez real | liquidity_trap | bi | 1h | BTC/ETH/SOL | 1h sweep near 4h level | mean/time | multi-TF level | fixed notional | OHLCV | holdout | P1 | alto | novo codigo | Expectancy melhora sem N baixo | Confluencia overfit |
| RB001 | T5 | Robustness | Walk-forward padrao para todo candidato | Edge deve sobreviver a folds temporais | validation | n/a | all | all | candidates | candidates | frozen | frozen | OHLCV | walk-forward | P0 | baixo | engine existente | Folds positivos e metricas estaveis | Um fold domina resultado |
| RB002 | T5 | Robustness | Final holdout nunca reutilizado | Evita promocao por iteracao | validation | n/a | all | all | candidates | candidates | frozen | frozen | final holdout | final holdout | P0 | baixo | validacao estatistica | Resultado preservado no holdout | Ajuste apos holdout invalida |
| RB003 | T5 | Robustness | Cross-asset validation | Edge estrutural nao deve ser ativo unico salvo tese explicita | validation | n/a | all | BTC/ETH/SOL | candidates | candidates | frozen | frozen | OHLCV | cross-asset | P0 | medio | engine existente | 2+ ativos ou razao causal para unico | Um ativo sem mecanismo |
| RB004 | T5 | Robustness | Cross-era validation | Evita single-window outlier | validation | n/a | all | all | candidates | candidates | frozen | frozen | 2024H2-2025H2 | cross-era | P0 | medio | engine existente | Passa em 2+ eras ou regime detector valida | So uma era |
| RB005 | T5 | Robustness | Monte Carlo trade shuffle | Mede dependencia de ordem e cauda | validation | n/a | all | all | trades | n/a | frozen | frozen | trade list | MC shuffle | P0 | baixo | engine existente | DD p95 aceitavel | Ruin risk alto |
| RB006 | T5 | Robustness | Block bootstrap por regime | Preserva clustering temporal | validation | n/a | all | all | trades | n/a | regime blocks | frozen | trades+regime | bootstrap | P1 | medio | novo codigo | Edge sobrevive a blocos | So shuffle simples passa |
| RB007 | T5 | Robustness | Fee stress 2x/3x | Custos reais variam e podem subir | validation | n/a | all | all | candidates | candidates | frozen | frozen | cost model | fee stress | P0 | baixo | engine existente | Net positivo em stress razoavel | Colapsa em 2x fee |
| RB008 | T5 | Robustness | Slippage stress por notional | Tamanho degrada fill | validation | n/a | all | all | candidates | candidates | frozen | notional ladder | cost model | slippage stress | P0 | medio | engine existente | Capacidade minima definida | Edge some em notional baixo |
| RB009 | T5 | Robustness | Spread stress variavel | Spread nao e constante em regime ruim | validation | n/a | all | all | candidates | candidates | frozen | frozen | spread proxy/data | spread stress | P1 | medio | dados adicionais | Sobrevive a spread p90 | Spread consome edge |
| RB010 | T5 | Robustness | Missing candle stress | Dados reais falham e resample pode distorcer | validation | n/a | all | all | candidates | candidates | frozen | frozen | OHLCV | missing candle stress | P1 | baixo | novo codigo | Resultado pouco sensivel | Sinais dependem de gaps |
| RB011 | T5 | Robustness | Latency stress next-open + delay | Execucao real pode atrasar | validation | n/a | all | all | candidates | delayed exit/entry | frozen | frozen | OHLCV | latency stress | P1 | medio | novo codigo | Sobrevive a 1-2 bars delay | Alpha depende de fill perfeito |
| RB012 | T5 | Robustness | Parameter perturbation local | Edge robusto nao depende de numero exato | validation | n/a | all | all | candidates | candidates | +/- local | frozen | OHLCV | perturbation | P0 | medio | engine existente | Vizinhanca preserva sinal | Colapsa com pequeno ajuste |
| RB013 | T5 | Robustness | Data snooping log por familia | Numero de tentativas precisa entrar na evidencia | validation | n/a | all | all | all tests | n/a | n/a | n/a | experiment log | audit | P0 | baixo | novo codigo | Todos fracassos registrados | Resultado sem denominador |
| RB014 | T5 | Robustness | Deflated Sharpe Ratio | Corrige multiplas tentativas e nao-normalidade | validation | n/a | all | all | candidates | n/a | frozen | frozen | returns | DSR | P1 | medio | validacao estatistica | DSR acima threshold definido | Sharpe deflated irrelevante |
| RB015 | T5 | Robustness | Probabilistic Sharpe Ratio | Mede probabilidade de superar benchmark | validation | n/a | all | all | candidates | n/a | frozen | frozen | returns | PSR | P1 | medio | validacao estatistica | PSR alto vs benchmark | PSR baixo apesar de PnL |
| RB016 | T5 | Robustness | White Reality Check por familia | Controla data snooping entre variantes correlacionadas | validation | n/a | all | all | family variants | n/a | frozen | frozen | returns | Reality Check | P2 | alto | validacao estatistica | Melhor variante segue significante | Vencedor perde significancia |
| RB017 | T5 | Robustness | Benchmark simple strategy comparison | Edge deve superar alternativa simples | validation | n/a | all | all | candidates | candidates | frozen | frozen | OHLCV | benchmark | P0 | baixo | engine existente | Supera B&H/flat/equal/stack | Nao supera baseline |
| RB018 | T5 | Robustness | Execution invariant audit | Sem causalidade correta nao ha resultado valido | validation | n/a | all | all | candidates | candidates | frozen | frozen | code/spec logs | audit | P0 | baixo | engine existente | Sem lookahead e fill fiel | Qualquer violacao invalida |
| XP001 | T6 | Exploratory | Funding carry + MR hybrid | Funding extremo pode pagar carry enquanto espera reversao | exploratory | adaptive | 1h/4h | BTC/ETH/SOL | funding + MR | time/mean | funding | fixed notional | funding + OHLCV | prereg + OOS | P3 | alto | dados adicionais + ADR antes de producao | Carry melhora retorno liquido | Funding nao causal/disponivel |
| XP002 | T6 | Exploratory | Order book imbalance predictor | Desequilibrio no livro pode antecipar sweep/fill | exploratory | adaptive | 1m/1h | BTC/ETH/SOL | imbalance | micro exit | depth | fixed notional | order book | forward | P3 | alto | dados adicionais + novo codigo | Edge apos latency/cost | Degrada com latency |
| XP003 | T6 | Exploratory | Liquidation data como regime de squeeze | Liquidations forcadas criam reversoes ou continuacao | exploratory | adaptive | 1h | BTC/ETH/SOL | liquidation spike | adaptive | liquidation data | fixed notional | liquidation feed | OOS | P3 | alto | dados adicionais | Melhora LQ traps | Feed indisponivel/overfit |
| XP004 | T6 | Exploratory | Cross-exchange premium | Deslocamento entre exchanges sinaliza fluxo | exploratory | adaptive | 1m/1h | BTC/ETH/SOL | premium zscore | mean/time | exchange spread | fixed notional | multi-exchange | OOS | P3 | alto | dados adicionais + novo codigo | Edge apos custos | Arbitragem ilusoria |
| XP005 | T6 | Exploratory | News/event blackout filter | Eventos exogenos elevam gap/latency risk | exploratory | adaptive | 1h | BTC/ETH/SOL | stack entries | base | event calendar | fixed notional | event data | forward | P3 | medio | dados adicionais | Reduz cauda sem matar edge | Eventos nao explicam perdas |
| XP006 | T6 | Exploratory | ML regime classifier restrito | Classificador pode combinar regimes sem grid manual | exploratory | adaptive | 1h | BTC/ETH/SOL | stack entries | base | ML regime | fixed notional | feature store | DSR + holdout | P3 | alto | novo codigo + validacao estatistica | Supera regras simples no holdout | Nao supera regra simples |
| XP007 | T6 | Exploratory | Meta-labeling de qualidade do sinal | Prever quais sinais executar reduz falsos positivos | exploratory | adaptive | 1h | BTC/ETH/SOL | stack signals | base | meta-label | fixed notional | labels causal | DSR + OOS | P3 | alto | novo codigo + validacao estatistica | Lift robusto vs signal strength simples | Data snooping evidente |
| XP008 | T6 | Exploratory | Options implied volatility regime | IV pode antecipar risco de cauda crypto | exploratory | adaptive | 1h/4h | BTC/ETH | stack entries | base | IV percentile | fixed notional | options data | OOS | P3 | alto | dados adicionais | Reduz cauda e melhora timing | IV indisponivel ou atrasada |
| XP009 | T6 | Exploratory | Stablecoin liquidity stress gate | Liquidez de stablecoins pode antecipar risk-off | exploratory | adaptive | 1h/4h | BTC/ETH/SOL | stack entries | base | stablecoin stress | fixed notional | external data | OOS | P3 | alto | dados adicionais + novo codigo | Risk-off detectado antes de DD | Sem causalidade direta |

## 15. Saida final

### Resumo executivo

O V2 reduz o roadmap de 1000 probes para 180 hipoteses preregistradas, com foco em mecanismo causal, invalidacao, robustez e utilidade operacional. A prioridade sai de "mais combinacoes" e vai para: regime detection, exit research, sizing controlado, portfolio construction, liquidity traps e falsificacao estatistica.

Nenhuma proposta deste documento aprova producao. Itens que alteram exit, sizing, risco, portfolio allocation, execution semantics ou dados de execucao real exigem ADR antes de producao.

### Principais mudancas em relacao ao roadmap antigo

- Reducao forte de grids parametricos.
- Cada teste tem mecanismo causal e criterio de invalidacao.
- Exits viram frente primaria, nao detalhe do engine.
- Sizing vira objeto de pesquisa separado e bloqueado para producao sem ADR.
- Portfolio passa a ser avaliado por drawdown, correlacao, turnover e contribuicao marginal.
- Regime detection e separado da estrategia para reduzir overfitting.
- Liquidity traps entram como nova fronteira causal.
- Robustez estatistica e stress de execucao passam a ser gates obrigatorios.

### Top 20 hipoteses mais promissoras

1. RM013 - BTC risk-off gate protege alt longs.
2. RM017 - Risk-off tri-asset ativa bear-avoidance trend.
3. RM018 - Regime de chop favorece BB/RSI width.
4. RM025 - Correlacao rolling alta reduz trades simultaneos.
5. RM034 - Gate de drawdown de B&H ativa bear-avoidance.
6. EX001 - Time stop curto melhora MR.
7. EX004 - ATR trailing stop reduz cauda.
8. EX009 - Break-even after MFE reduz losers tardios.
9. EX011 - Adverse excursion exit elimina trades quebrados.
10. EX016 - HTF reversal exit protege longs.
11. EX017 - HTF reversal exit protege shorts.
12. PS003 - Vol targeting por ativo reduz concentracao em SOL.
13. PS005 - Risk parity por ativo melhora diversificacao.
14. PS017 - Cap de exposicao simultanea por ativo.
15. PF004 - Correlation cap 0.7 reduz redundancia.
16. PF012 - Separacao por ativo reduz beta duplicado.
17. PF024 - Add-one candidate testa valor marginal.
18. LQ001 - Falso rompimento da maxima anterior reverte.
19. LQ002 - Falso rompimento da minima anterior reverte.
20. LQ025 - Close back inside range e melhor que wick apenas.

### Top 20 hipoteses que devem ser testadas primeiro

1. RB018 - Execution invariant audit.
2. PF001 - Equal weight stack como benchmark formal.
3. PF023 - Ablation one-combo-out mede dependencia.
4. RM013 - BTC risk-off gate protege alt longs.
5. RM018 - Regime de chop favorece BB/RSI width.
6. RM025 - Correlacao rolling alta reduz trades simultaneos.
7. EX001 - Time stop curto melhora MR.
8. EX004 - ATR trailing stop reduz cauda.
9. EX009 - Break-even after MFE reduz losers tardios.
10. EX033 - Exit de cauda por ATR hard stop como benchmark.
11. PS027 - Baseline fixed_notional 5 niveis como sensitivity.
12. PS003 - Vol targeting por ativo reduz concentracao em SOL.
13. PS017 - Cap de exposicao simultanea por ativo.
14. PF004 - Correlation cap 0.7 reduz redundancia.
15. PF024 - Add-one candidate testa valor marginal.
16. LQ001 - Falso rompimento da maxima anterior reverte.
17. LQ002 - Falso rompimento da minima anterior reverte.
18. LQ025 - Close back inside range e melhor que wick apenas.
19. RB001 - Walk-forward padrao para todo candidato.
20. RB012 - Parameter perturbation local.

### Hipoteses que provavelmente devem ser descartadas do roadmap antigo

- Novos grids amplos de BB `window` e `num_std` sem mecanismo novo.
- Novos grids amplos de RSI `period` e thresholds se nao forem sensitivity local.
- Reabertura de MR 10m/15m/30m sem microestrutura nova.
- Keltner/zscore sem regime detector novo.
- Donchian amplo sem filtro de breakout/failure causal.
- Supertrend/MA 10m fora de bear alt sem regime detector.
- AND de filtros quando uma perna isolada ja falha ou e redundante.
- Asset expansion LINK/DOT/AVAX sem triagem de liquidez/regime.
- ML/exotic feature flags sem dataset e protocolo estatistico.
- Variantes que so mudam ativo/janela/parametro sem nova hipotese.

### Riscos metodologicos restantes

- Mesmo 180 hipoteses ainda exigem controle de multiplas tentativas.
- Regime detection pode virar data snooping se treinado no mesmo holdout.
- Exits e sizing podem melhorar drawdown apenas por reduzir exposicao, nao por edge.
- Liquidity traps usando OHLCV sao proxies; ordem real pode degradar o resultado.
- Portfolio otimizado pode overfit correlacao historica.
- Dados adicionais podem ter latencia, survivorship, buracos ou incompatibilidade com execucao real.

### Proximos passos objetivos

1. Registrar ADR de preregistro da Fase 1 do V2, apontando para este documento.
2. Congelar discovery/validation/final holdout antes de qualquer backtest V2.
3. Rodar apenas auditorias e baselines de portfolio que nao alteram estrategia.
4. Executar primeiro os testes com `engine existente` e menor risco de codigo novo.
5. Criar ADR separado para qualquer implementacao de exit layer, sizing layer, portfolio allocator ou liquidity trap engine.
6. Registrar todos os fracassos e encerrar familias quando criterios de invalidacao forem atingidos.
