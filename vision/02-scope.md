# 02 — Scope

> **Layer:** Target.
> **Purpose:** define what is in, what is out, and what the modules of the system are.
> **Agent rule:** a feature request that does not map to a module below must trigger a conversation with the user before being built.

---

## In scope — modules

7 módulos. Regra de acoplamento: `strategies` depende **apenas** de `data`; regime é insumo **opcional** injetado via `backtest`/`validation`, não dependência rígida do catálogo.

### Module: `data`

- **What it does:** ingestão, validação, normalização e versionamento de dados de mercado.
- **Key capabilities:**
  - download/importação OHLCV multi-ativo
  - múltiplos timeframes
  - reamostragem
  - detecção de gaps
  - validação de integridade
  - datasets versionáveis
- **Depends on:** nenhum

### Module: `strategies`

- **What it does:** catálogo de estratégias com interface comum e parâmetros auditáveis.
- **Key capabilities:**
  - interface padrão long/short
  - stop fixo / ATR / trailing
  - takes parcial e final
  - break-even
  - pyramiding opcional
  - filtros configuráveis (tendência, volatilidade, sessão)
  - famílias iniciais de estratégia (breakout, momentum, pullback, mean reversion, liquidity sweep, continuação, expansão de range, snowball, falha de rompimento, híbrida)
- **Depends on:** `data`

### Module: `regimes`

- **What it does:** classificar o mercado em regimes auditáveis e reutilizáveis.
- **Key capabilities:**
  - tendência forte de alta
  - tendência forte de baixa
  - lateral de baixa volatilidade
  - lateral de alta volatilidade
  - compressão
  - expansão
  - pânico
  - euforia
  - exposição do regime como feature auditável para outros módulos
- **Depends on:** `data`

### Module: `risk`

- **What it does:** controlar exposição, orçamento de risco e mecanismos de defesa (governança, separada do motor de simulação).
- **Key capabilities:**
  - risco por trade
  - risco por dia
  - risco por ativo
  - risco por estratégia
  - risco agregado
  - equity guard
  - escada de equity
  - trailing de equity
  - kill switch
  - lockout
  - risco de liquidação aproximada
- **Depends on:** `data`

### Module: `backtest`

- **What it does:** simulação causal e realista da execução da estratégia.
- **Key capabilities:**
  - ordens market / stop / limit simplificada
  - maker/taker fees
  - slippage
  - funding
  - spread sintético
  - expiração de sinal
  - latência opcional
  - leverage até 10x
  - enforcement anti-lookahead
  - integração opcional com `regimes` quando a estratégia quiser usar
- **Depends on:** `data`, `strategies`, `risk`, `regimes`

### Module: `validation`

- **What it does:** validar robustez estatística e resistência da estratégia. Nada promove ao ranking sem passar por aqui.
- **Key capabilities:**
  - walk-forward
  - out-of-sample
  - Monte Carlo
  - perturbação de fees/slippage
  - parameter stability
  - robustness score
  - flags de fragilidade (`CURVE FIT PROVÁVEL`, `FRÁGIL`, `NÃO GENERALIZA`)
  - grid search
  - random search
- **Depends on:** `backtest`

### Module: `ranking`

- **What it does:** calcular métricas finais, score multiobjetivo e saídas comparativas. Duas subáreas internas claras: **scoring** (cálculo de métricas + score multiobjetivo + leaderboard) e **reporting** (relatórios, comparações, export).
- **Key capabilities:**
  - métricas de performance e risco (retorno, drawdown, Sharpe, Sortino, Calmar, profit factor, expectancy, hit rate, ulcer index, exposure time, turnover, risco de ruína aproximado, robustness por regime etc.)
  - score multiobjetivo com pesos configuráveis
  - leaderboard
  - comparação entre estratégias
  - relatórios comparativos
  - exportação de resultados
- **Depends on:** `validation`, `regimes`
- **Internal split (documentado, não extraído agora):** `scoring` vs `reporting`. Pode ser extraído em módulo próprio depois se crescer demais.

### Dependency graph

```
data ───┬──> strategies ──┐
        ├──> regimes ─────┤
        └──> risk ────────┤
                          └──> backtest ──> validation ──> ranking
                                                             ^
                          regimes ─────────────────────────┘
```

**Notas de acoplamento deliberadas:**

- `risk` **não** é mesclado em `backtest`: risk é governança/orçamento de exposição; backtest é motor de simulação. Mesclar cedo vira classe monolítica.
- `metrics` **não** é módulo separado agora: vive dentro de `ranking.scoring`. Extrair só se crescer demais.
- `strategies` **não** depende de `regimes`: estratégia declara filtros; regime é injetado pelo backtest quando aplicável. Desacoplamento proposital.

---

## Out of scope

Fronteira estrutural: coisas que o Alpha Forge **não faz**, mesmo que alguém peça. "Gerador mágico de estratégia campeã" não aparece aqui — vive como princípio em `vision/01-product.md` (é postura metodológica, não item de escopo modular).

- **SaaS multi-tenant (billing, auth, múltiplos clientes)** — Razão: alvo é uso técnico local; multi-tenant é outro produto.
- **Venda de sinais / copy-trade / feed público** — Razão: o laboratório produz inteligência interna; produto público mudaria risco, distribuição e implicações regulatórias.
- **Market making / HFT (latência sub-segundo)** — Razão: a arquitetura é orientada a candles e estratégias de minutos a dias; HFT exigiria outra pilha técnica (orderbook tick, coloc, C++).
- **Derivativos exóticos (opções, inverse futures exóticos, estruturados)** — Razão: exigem modelagem de payoff, risco e execução muito diferente do foco atual (spot + perpétuos/futuros lineares).
- **Reconstrução tick-a-tick de orderbook** — Razão: a pesquisa-alvo parte de OHLCV e dados agregados; microestrutura profunda é outro projeto.
- **Journaling discricionário** — Razão: o laboratório trata apenas estratégias formalizáveis em código.
- **Plataforma genérica de ML/AutoML ou pesquisa pesada de modelos** — Razão: o produto é um laboratório de estratégias e validação quantitativa; ML pode ser usado pontualmente como ferramenta auxiliar (ex: classificador de regime), mas não é eixo central do sistema. Ficam fora: pipelines de treino pesados, feature stores, tuning de redes neurais, repositório de modelos.

## Explicitly deferred (not out of scope, just not now)

Pertence ao produto, mas fica para fase posterior. Não trazer nada disto para in-scope imediato.

- **`paper-trade` / live integration via `ccxt`** — Razão: o núcleo é pesquisa e validação; paper/live só faz sentido depois do pipeline estar maduro. Entra na Fase 6 do roadmap.
- **Classificador de regime via ML** — Razão: a primeira versão deve usar heurísticas auditáveis (ATR, ADX, volatilidade realizada); ML só entra se houver ganho claro.
- **Interface operacional / dashboard interativo** — Razão: relatórios estáticos e notebooks bastam no início; dashboard vivo (ex: Streamlit/Panel) entra depois se houver necessidade real.
- **Expansão para outros mercados (ações, forex, commodities)** — Razão: foco inicial é cripto; arquitetura deve permitir expansão, mas não é objetivo ativo.
- **Módulo `metrics` separado de `ranking.scoring`** — Razão: manter acoplado no começo reduz fragmentação prematura; extrair depois se crescer.
- **Suporte multi-exchange além da primeira integração** — Razão: começar com uma integração-alvo reduz complexidade, diferenças de contrato e manutenção; expandir cedo só multiplica custo sem validar arquitetura.
- **Execução em cloud / jobs distribuídos / storage remoto** — Razão: a primeira versão deve priorizar simplicidade local e reprodutibilidade forte; escalar para cloud, filas, orquestração remota ou storage distribuído faz sentido só depois do núcleo estar maduro.

---

## Scope change protocol

When a user requests something that is not in the module list:

1. Ask whether it belongs to an existing module (add as capability) or needs a new module.
2. If it conflicts with "out of scope," surface the prior reason and ask for explicit override.
3. Update this file in the same commit as the code change.

---

## Interview checklist

- Every module has a name, responsibility, and at least one capability.
- Every out-of-scope item has a reason.
- No module depends on a module that does not exist.
