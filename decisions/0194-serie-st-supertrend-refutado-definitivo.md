# 0194 — Série ST closeout: SuperTrend refutado definitivo (4 runs, naked + width)

**Status:** Accepted — SuperTrend arquivado. Família trend-follow primária confirmada impraticável em AF 1h crypto.
**Date:** 2026-04-21
**Deciders:** Usuário ("tenta outras estrategias ai, ta foda") + agente
**Relates to:** ADR-0193 (pré-reg), Padrão 45 (filter normaliza mas não cria edge)

## Resumo executivo

SuperTrend 10/3 bidirectional naked 2025-H1 BTC/ETH/SOL: **Sharpe todos negativos (-1.19 a -1.94), PnL -5% a -9%, 70+ trades cross-asset**. Probe Fase 2 BTC +width filter: **Sharpe ainda -1.69 com 12 trades**. Filter cortou amostra em 83% sem reverter negatividade. **Refutada em todas as dimensões acessíveis naked/filtered.**

## Resultados Fase 1 (ST.1-3)

| Tag | Combo | Trades | Sharpe | PnL% |
|---|---|---:|---:|---:|
| ST.1 | BTC supertrend 10/3 bi 2025-H1 | 72 | **-1.938** | -5.34 |
| ST.2 | ETH idem | 76 | **-1.185** | -5.84 |
| ST.3 | SOL idem | 70 | **-1.651** | -8.80 |

**Gate 2/3 Sh≥1.5 AND trades≥30: 0/3** — refutada.

## Resultado Fase 2 (ST.4 probe opcional Padrão 45)

| Tag | Combo | Trades | Sharpe | PnL% |
|---|---|---:|---:|---:|
| ST.4 | BTC supertrend 10/3 + bollinger_width(30,1.5,300) bi 2025-H1 | 12 | **-1.689** | -2.23 |

Filter cortou 72→12 trades (83% redução). Sharpe permanece negativo. Padrão 45 confirma-se mais uma vez — **filter normaliza/reduz variance mas não cria edge onde o engine não tem**.

## Interpretação

### Hipótese falhou estrutural e empiricamente

ADR-0193 previu prior ~25-35% de pass. Downside reconhecido: "SuperTrend notório por whipsaws em chop — muitos fake breakouts. 1h crypto tem ruído alto". **Downside realizou-se fortemente** — Sharpe -1.5 médio indica não só ausência de edge, mas **anti-edge**: o engine entra late/sai early no pior ponto do movimento em crypto 1h.

Mecanismo provável: ATR-band trailing reage ao close recente, flipping em pullbacks normais dentro de trends reais. Em 1h crypto, volatilidade intra-trend é alta (5-15% swings comuns), suficiente para disparar flip e invalidar entrada subsequente.

### Padrão 45 reforçado com N=3 engines

| Engine | Naked outlier | +width filter | Normaliza? | Edge ≥ 1.5? |
|---|---|---|---|---|
| DE (trend_htf 1d) | ETH 2025-H1 Padrão 41 | n/a | — | — |
| KE (Keltner) | ETH 2025-H1 Sh=2.40 | Converge 1.16-1.24 | Sim | Não |
| ST (SuperTrend) | — cross-asset fail | Trades 12, Sh -1.69 | Trivialmente (cortou) | Não |

Padrão 45 agora validado em 3 engines consecutivos. **Formalização definitiva**: filter canônico é ferramenta de diagnóstico (normaliza/reduz sample), não de criação de edge.

### Trend-follow primário em AF 1h crypto: insuficiente evidência cross-engine

SuperTrend foi o primeiro engine trend-follow primário testado (trend_htf 1d é filter; MACX arquivado; Donchian arquivado). Pyramid v4 foi volume-amplifier de MR, não trend-follow puro. **3 paradigmas trend-follow ortogonais tentados (Donchian breakout, MACX, SuperTrend ATR-band) = 3 arquivados**. Padrão candidato novo: **"Trend-follow primário não sobrevive em crypto 1h — noise/whipsaw domina estrutural"**. N=3 suficiente para consolidar tendência, não formalizar padrão ainda.

## Consolidação autopilot round 3+1 (este)

Pós-ADR-0192 (autopilot parado formalmente + Padrão 47 round 3), usuário destravou: "tenta outras estratégias ai, ta foda.. nao to conseguindo muita coisa no bot binance" → agente decidiu dev SuperTrend (novo paradigma ortogonal ao stack 100% MR).

Dev + runs:
- Engine 136 linhas + __init__
- CLI wire (10 edits em app.py)
- 5 unit tests passing
- 4 runs (ST.1-4): 0 promoções, confirma refutação Fase 1 + Fase 2

**Total pós-ADR-0192**: 4 runs, 0 promoções. Autopilot cumulativo desde ADR-0096: **68 runs, 0 promoções**.

## Decisão

- **SuperTrend arquivado** em todas as dimensões testadas (naked + width). Código preservado em `src/alpha_forge/strategies/families/supertrend/` como dormente (custo manter = zero, revisitar se nova hipótese emergir — ex: SuperTrend 4h timeframe, SuperTrend + MR composite).
- **Stack 13 combos em 9 manifest files inalterado** — nenhuma edição de manifest, nenhum impacto no bot.
- **Runtime contract faithful (v3) permanece canônico** — nunca foi needed v4 nem composite.
- **Padrão 45 formalizado** (atualização ADR-0172): N=3 engines confirmam — filter normaliza mas não cria edge.

## Opções remanescentes para autopilot

Paradigmas dev-leve/cheap efetivamente exauridos. Remanescentes com dev real:

1. **Ichimoku** — trend-follow multi-timeframe nativo. Dev ~3-4h. Prior: baixo (mesmo paradigma trend-follow 3× refutado, mas multi-TF pode mudar comportamento).
2. **ADX-filtered MR** — filter ADX como proxy de "trend strength" para habilitar MR apenas em chop (ADR-0180 deu pista disso). Dev ~2h. Prior médio (~30%): é essencialmente tunar stack MR atual com seletor de regime diferente.
3. **Cross-sectional momentum** — dev pesado (~1 dia), requer multi-asset framework. Prior incerto.
4. **Novo asset 1h** — BNB/ADA/XRP em combos aprovados. Prior baixo (Padrão 45 + BTC/ETH/SOL cobrem liquidez top).
5. **Bot live paper-trade** — zero-dev, o usuário já está nisso.
6. **Parameter sweep em combos aprovados** — overfit risk, não recomendado.

**Agente recomenda**: usuário decide. EV de novos engines é **persistentemente baixo** após 3 paradigmas trend-follow + 4 paradigmas MR arquivados nesta janela. Foco natural é **bot paper-trading stack atual** enquanto monitora divergência de premissa — consistente com `feedback_strategy_research_cycle` (bot só reporta divergência, AF pesquisa offline).

Se usuário quer mais 1 iteração cheap: ADX-filtered MR é a frente com maior prior custo-benefício.

## Não-alvo

- Não testar SuperTrend 4h/períodos maiores (diminishing returns, 4× comboteste pessimista)
- Não implementar Ichimoku sem sinal forte de user (dev pesado vs prior baixo)
- Não tocar stack 13 combos

## Ação executada

- ✅ ADR-0193 pré-reg SuperTrend engine
- ✅ Engine + CLI + 5/5 unit tests
- ✅ 4 runs (ST.1-3 Fase 1 + ST.4 Fase 2 probe)
- ✅ Padrão 45 formalização N=3
- ✅ ADR-0194 closeout (este)
- ⏭️ STATE.md update
- ⏭️ Bridge inbox: nenhuma notificação (não muda decisão do bot; stand-down permanece)
