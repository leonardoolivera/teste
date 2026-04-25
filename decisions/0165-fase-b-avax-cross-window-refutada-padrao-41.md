# 0165 — Fase B closeout: AVAX cross-window 2025-H2 refutado, Padrão 41 dispara, Frente 4 arquivada

**Status:** Accepted — refutação. Frente 4 arquivada sem promoção.
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0164 (pré-reg), ADR-0163 (Fase A), Padrão 41 (janela-específica)

## Resultado

| Tag | Combo | Trades | 2025-H1 Sh | 2025-H2 Sh | PnL% | Gate |
|---|---|---:|---:|---:|---:|:---:|
| DD.1 | AVAX rsi+width | 90 | 1.64 | **0.377** | 1.76 | ❌ |
| DD.2 | AVAX rsi+trendhtf | 54 | 1.77 | **0.662** | 2.87 | ❌ |

Gate: Sh ≥ 0.8 AND trades ≥ 40. **0/2 passam.**

## Avaliação

**Padrão 41 dispara**: edges de AVAX em 2025-H1 (Sh 1.64 e 1.77) colapsam em 2025-H2 para Sh 0.38 e 0.66. Degradação de ~75% em Sharpe cross-window. Mesma assinatura observada em CZ15 (SOL BB ns=2.0) e CZ18 (BTC RSI p=21): outlier 1-janela que não generaliza.

## Interpretação

### AVAX 2025-H1 teve regime favorável específico

2025-H1 foi período de downtrend moderado em AVAX pós-topo 2024-Q4 ($50 → $20). RSI short + filter capturou movimento único. 2025-H2: AVAX consolidou em range $15-25, signals RSI extremos foram menos fiáveis. Edge era regime-downtrend, não estrutural.

### Padrão 43 vs Padrão 41: tensão

Padrão 43 dizia **asset novo é dimensão dominante** de diversificação/descoberta. Verdadeiro — AVAX 2025-H1 achou Sh>1.5 em 2 combos (vs 0 em DOT/LINK). Mas **Padrão 41 bloqueia** porque 1 janela não valida. Os dois padrões não conflitam: 43 identifica **onde procurar**, 41 valida **se vale promover**.

Insight consolidado: **ingest de novo asset eleva probabilidade de encontrar outliers H1-específicos, mas outliers ainda precisam cross-window.** Expectativa Fase A (prior: 1-2 combos promovíveis) confirmou-se pessimista — **0 promovíveis** após gate rigoroso.

### Frente 4 balanço

- Compute gasto: ingest (12 datasets 2025-H1 + 1 AVAX 2025-H2) + 11 runs (9 DC + 2 DD) ≈ 30-40 min
- Resultado: **0 promoções, 0 mudanças de manifest**
- Valor de informação: **alto negativamente** — confirma que toolkit atual (bol/rsi width/trendhtf short) é ótimo local para BTC/ETH/SOL e não generaliza trivialmente para alts sem tuning específico

## Decisão

- **Nenhuma edição de manifest**
- **Frente 4 arquivada** após Fase B
- **Datasets DOT/AVAX/LINK 2025-H1 + AVAX 2025-H2 mantidos** no datasets.yaml (custo zero armazenar; podem ser úteis para pesquisa futura se toolkit evoluir)
- Fase C cancelada (não há candidatos para cross-era)

## Aprendizados (para futuro)

1. **Alts com toolkit canônico**: prior ajustado de "1-2 promovíveis" para **"~0 sem tuning específico"**. Canônicos w=20/30 BB + p=14 RSI são otimizados para BTC/ETH/SOL; alts precisariam sweep dedicado.

2. **BB em alts**: 3/3 negativos. Window 20 é muito rápido para vol de alts. Se re-abrir, começar em w=25-35.

3. **RSI em alts**: 2/3 assets (DOT/AVAX) tiveram Sh > 1 em alguma config 2025-H1. Sugere RSI é mais transferível entre assets que BB (mean-reversion BB depende de stationary vol; RSI é momentum-ratio, mais portável).

4. **Ingest é barato, runs caros**: ingest foi ~segundos; runs demoram. Estrutura futura: sempre separar ingest + screening leve (1-2 runs/asset) antes de committar ao grid completo.

## Ação executada

- ✅ Ingest AVAX 2025-H2
- ✅ 2 runs DD
- ✅ ADR-0165 closeout
- ✅ Frente 4 arquivada

## Não-alvo

- Não re-abrir alts sem hipótese estrutural nova
- Não ingestir 2024 (Fase C cancelada)
- Não promover AVAX com ADR-override (magnitude de falha é clara)

## Próximas direções possíveis (pós-Frente 4)

Stack continua com 13 combos, parcialmente diversificado (mean corr H1 +0.35, H2 +0.38), sem upgrades 1-knob disponíveis. Próximas frentes **não-óbvias**:

1. Tuning de params específico para alts (BB window maior, RSI bounds diferentes)
2. Cross-timeframe (HTF signals + LTF execution) — nunca explorado formalmente
3. Revisar combos antigos com Padrão 43 em mente (consolidar redundâncias engine-only?)
4. Stop de pesquisa ativa — aceitar stack atual como estado estável
