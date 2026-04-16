# 01 — Product

> **Layer:** Target. What we want to be, not what exists.
> **Changes:** rarely, and only with explicit user approval.
> **Agent rule:** if a field below contains `{{PLACEHOLDER}}`, interview the user before proceeding. Do not guess.

---

## Name

Alpha Forge

## One-sentence description

Laboratório de pesquisa, backtest rigoroso, validação estatística e ranking de estratégias de trading cripto com alavancagem de até 10x, projetado para descobrir setups agressivos sem mascarar fragilidade com overfitting.

## The problem

O Alpha Forge resolve a dor de **diferenciar edge real de ilusão estatística** em estratégias de trading cripto agressivas. Hoje, traders sistemáticos e desenvolvedores de bots validam ideias de forma fragmentada — usando backtests isolados, ferramentas parciais e processos pouco comparáveis — o que leva a overfitting, falsa confiança e estratégias que quebram em live quando expostas a fees, slippage, funding e mudanças de regime.

Como é hoje, sem o Alpha Forge:

- É fácil criar uma estratégia que *parece* boa: basta achar um recorte bonito do passado.
- Falta um processo sério de comparação, stress e ranking — então não há como saber se o que parece "campeã" tem edge de verdade ou se é só curva ajustada.
- A validação é remendada: algumas ferramentas cobrem backtest, outras cobrem parâmetros, outras cobrem execução — nenhuma entrega, num único laboratório, comparação justa entre estratégias + robustez + ranking multiobjetivo + stress com custos reais + detecção clara de fragilidade/overfitting.
- Resultado: estratégias sobrevivem ao backtest e morrem em live.

## Target users

Usuários-alvo (todos tecnicamente proficientes, operando cripto com alavancagem):

- **Trader sistemático independente** — desenvolve e opera estratégias por conta própria; precisa separar edge real de ilusão antes de arriscar capital.
- **Pesquisador de estratégias** — explora famílias de setups (breakout, momentum, mean reversion etc.) e precisa compará-las sob condições idênticas, com ranking multiobjetivo.
- **Desenvolvedor de bot** — implementa estratégias em código e precisa estressar a lógica contra fees, slippage, funding e regimes distintos antes de ligar em live.
- **Operador agressivo** — busca crescimento explosivo de capital com alavancagem até 10x, mas quer evidência rigorosa de robustez antes de expor a conta.

## Value proposition

Diferenciais centrais do Alpha Forge frente a frameworks de backtest genéricos (Freqtrade, Backtrader, vectorbt nu), plataformas SaaS (3Commas, Coinrule, TradingView Pine) e scripts caseiros. Listados em ordem de prioridade:

1. **Validação anti-overfitting embutida** — o pipeline padrão inclui walk-forward, out-of-sample, Monte Carlo, perturbação de custos e flags automáticas de fragilidade, para separar edge real de ilusão estatística. Não é extensão opcional: estratégia que não passa pelo pipeline não entra no ranking.
2. **Stress de custos reais por default** — maker/taker fees, slippage, funding e spread sintético entram por padrão nos testes, e a estratégia precisa sobreviver a perturbações desses atritos para ser promovida. Backtest "limpo" não é aceito como evidência.
3. **Classificação por regime de mercado** — cada estratégia é medida por regime (tendência forte alta/baixa, lateral de alta/baixa vol, compressão, expansão, pânico, euforia) e pode ser bloqueada onde é estruturalmente fraca, evitando médias enganosas no agregado.
4. **Engine de risco para alavancagem agressiva** — o laboratório suporta até 10x com controles rígidos de risco por trade, dia, ativo, estratégia e portfólio, além de equity guard, kill switch, lockout e estimativa de risco de liquidação aproximada.
5. **Ultra-agressividade honesta** — o Alpha Forge procura setups explosivos sem esconder o custo disso, marcando explicitamente estratégias frágeis, não generalizáveis ou propensas a curve fitting. Ao contrário de frameworks neutros, admite o trade-off risco/retorno abertamente.

## Non-goals

Coisas que o Alpha Forge **não faz**, mesmo que alguém peça. Nota de escopo: o foco inicial é cripto; expansão futura para outros mercados não está proibida, mas não é objetivo do produto neste momento.

- **Não é execução em produção automatizada 24/7** — o núcleo do Alpha Forge é pesquisa, validação e ranking; paper/live pode existir depois, mas não define o produto.
- **Não é uma plataforma SaaS multi-tenant** — o alvo é uso técnico local por um operador ou pequena equipe, não produto com billing, auth e múltiplos clientes.
- **Não vende sinais nem copy-trade** — o laboratório gera inteligência interna para decisão do próprio operador.
- **Não faz market making nem HFT** — o foco está em estratégias sistemáticas agressivas de minutos a dias, não em latência extrema.
- **Não opera derivativos exóticos** — o escopo cobre spot e perpétuos/futuros lineares, não opções nem estruturas mais complexas.
- **Não faz scraping nem reconstrução tick-a-tick de orderbook** — o foco base é OHLCV e dados agregados compatíveis com pesquisa robusta.
- **Não promete retornos** — mede edge, fragilidade e robustez; não garante performance futura.
- **Não substitui journaling discricionário** — não é diário de trades manuais nem ferramenta de reflexão subjetiva do operador.
- **Não é uma plataforma genérica de ML/AutoML** — pode usar ML pontualmente (ex. classificador de regime), mas não vira framework amplo de treinamento de modelos.
- **Não é um "gerador mágico de estratégia campeã"** — o objetivo é invalidar ilusões e ranquear hipóteses com honestidade estatística, não fabricar promessas.

## Definition of success

O Alpha Forge será considerado bem-sucedido quando cumprir, no mínimo, os seguintes critérios mensuráveis:

- **Cobertura e repetibilidade do pipeline:** rodar backtest + walk-forward + Monte Carlo + stress de custos de ponta a ponta em **< 10 min** para 1 estratégia, 1 ativo, 1 timeframe e 2 anos de histórico, em ambiente local de desenvolvimento padrão. _(TBD: calibrar o alvo de tempo na fase `building` — depende de hardware e volume de dados; tratar 10 min como meta inicial, não como limite rígido.)_
- **Facilidade de expansão:** adicionar uma nova estratégia ao catálogo em **≤ 1 hora** de trabalho humano, incluindo implementação, registro e execução da validação padrão.
- **Detecção de fragilidade:** **100%** das estratégias promovidas no ranking passaram por walk-forward, Monte Carlo e perturbação de fees/slippage — sem exceção.
- **Sinalização de overfitting:** identificar e marcar como `CURVE FIT PROVÁVEL`, `FRÁGIL` ou `NÃO GENERALIZA` **≥ 95%** das estratégias deliberadamente superajustadas em benchmarks sintéticos de fragilidade.
- **Qualidade e estabilidade do ranking:** comparar **≥ 10 estratégias** simultaneamente, com pesos configuráveis, e produzir resultados reprodutíveis no mesmo dataset e configuração.
- **Utilidade prática para decisão:** operador consegue, a partir dos relatórios e ranking, promover ou descartar uma estratégia em **≤ 30 min** de leitura.
- **Capacidade real de produzir candidatas sérias:** ao menos **3 famílias de estratégias** rodando ponta a ponta até score final, e ao menos **1 estratégia candidata** que sobreviva a walk-forward + Monte Carlo + stress de custos em **≥ 2 regimes distintos**.

## Principles

Núcleo moral do Alpha Forge. Quando um pedido futuro contradiz um princípio, o princípio vence — a menos que o usuário sobreponha explicitamente.

- **Honestidade estatística sobre performance bonita** — quando houver conflito entre um resultado impressionante e rigor metodológico, vence o rigor. Nenhuma métrica promocional sobe sem sobreviver ao pipeline de validação.
- **Custo real antes de retorno bruto** — fees, slippage, funding e atritos de execução entram por padrão; backtest "limpo demais" não serve como evidência séria.
- **Sem lookahead, nunca** — qualquer uso direto ou indireto de dados futuros é defeito crítico do sistema e deve ser detectado e bloqueado pela infraestrutura.
- **Ranking multiobjetivo, não monobjetivo** — lucro isolado não define qualidade; o score final deve combinar retorno, drawdown, robustez fora da amostra, estabilidade paramétrica, sensibilidade a custos, risco de ruína e consistência por regime.
- **Reproduzível ou não aconteceu** — todo resultado precisa poder ser reproduzido a partir de configuração, código e dataset versionado; sem isso, o resultado não tem legitimidade.
- **Flags explícitas de fragilidade** — sinais de overfitting, instabilidade ou não generalização devem ser marcados de forma visível e legível, nunca escondidos por médias bonitas.
- **Agressividade com controles duros, nunca sem eles** — o sistema pode buscar setups explosivos e operar até 10x, mas sempre sob orçamentos rígidos de risco, equity guard, kill switch e lockout.
- **Preferir simples e auditável a sofisticado e opaco** — quando duas abordagens entregarem resultado semelhante, vence a mais compreensível, rastreável e fácil de auditar.

_(Disciplina operacional — "vision antes de implementação" e "separação estrita entre aspiração e realidade" — não fica aqui: vive em `AGENTS.md` e na estrutura do template. São regras de processo, não princípios do produto.)_

---

## Interview checklist (for the agent)

Before this file is considered complete, every placeholder must be filled. If the user cannot answer one, mark it `TBD — needs research` and list it in `STATE.md` as a blocker. Do not leave raw `{{PLACEHOLDER}}` markers.
