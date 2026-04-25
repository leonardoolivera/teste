# 0169 — Assessment: novos engines (zscore MR, vol breakout) — escopo e viabilidade

**Status:** Assessment — decisão pendente.
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** Todos os ADRs de séries CZ6-9 (MACX refutado), CY (Donchian refutado)

## Motivação

Após todas as frentes 1-knob, cross-filter, AND composition, alts, consolidação, cross-timeframe terem sido exauridas no toolkit atual, **nenhum upgrade está acessível sem novo engine**. Stack 13 combos é estável, parcialmente diversificado (mean corr +0.35/0.38), zero edge adicional descoberto em sweeps baratos.

## Engines implementadas

`src/alpha_forge/strategies/families/`:
- `bollinger` — live, 4 eixos sensibilizados (Padrão 42)
- `rsi` — live, period/bounds sensibilizados (CZ10-18)
- `donchian` — refutada em CY (2026-04-20)
- `ma_crossover` — refutada em CZ6-9 (toda a família MACX)
- `dummy` — placeholder de tests

**Nenhum engine novo pronto para validation-only sweep.**

## Candidatos a novos engines

### Candidato A: zscore mean-reversion

**Design**: signal = zscore(close, window) = (close - mean) / stdev em janela rolante. Entry short quando zscore > +threshold (extremo alto); entry long quando zscore < -threshold. Exit quando zscore cruza 0.

**Vs Bollinger**: BB usa bandas (mean ± num_std × std). zscore é a **mesma matemática** em forma diferente (thresholds fixos vs bandas relativas). Diferença prática: zscore com threshold fixo tem **semântica discreta** (cruzou +2.0?), BB tem **semântica contínua** (preço acima/abaixo da banda?). Exit policy difere: BB exita na volta para média; zscore exita no zero-crossing.

**Risco**: zscore pode ser ~90% redundante com BB. Padrão 43 sugere que combos mesma asset+filter+direção com engines diferentes correlacionam +0.6. zscore vs BB é caso extremo — mesma fórmula, só reembrulhada. Expectativa: corr +0.8+.

**Custo implementação**: ~100-150 linhas em `src/alpha_forge/strategies/families/zscore/strategy.py` + testes. ~2-4 horas de código.

**Prior de payoff**: baixo. Não destravar dimensão nova se matematicamente redundante com BB.

### Candidato B: volatility breakout (Opening Range / NR7)

**Design**: entry long quando close > max(highs[-N:]) em janela fixa; short quando close < min(lows[-N:]). Não confundir com donchian (que usa high/low do channel em breakout-channels clássico — ~mesma lógica, já refutado).

**Vs Donchian**: ~idêntico. CY já testou donchian 20/10 e refutou integralmente.

**Risco**: 95% redundante com donchian.

**Custo**: ~80 linhas.

**Prior de payoff**: muito baixo.

### Candidato C: ATR expansion / compression (Keltner-like)

**Design**: signal = posição do preço vs envelope EMA ± ATR×k. Entry em compression+breakout ou expansion reversion.

**Vs Bollinger**: BB usa desvio padrão; Keltner usa ATR. ATR é mais robusto a spikes (median-like) vs stdev (outlier-sensitive). Pode dar edge em regimes de alta volatilidade discreta (flash crashes) onde BB fica "tonta" por outliers.

**Risco**: em crypto 1h com vol relativamente persistente, ATR vs stdev difere marginalmente. Prior: corr com BB ~+0.7.

**Custo**: ~120 linhas.

**Prior de payoff**: baixo-médio. Único candidato com **hipótese estrutural diferenciável** (robustez a outlier).

### Candidato D: cross-sectional momentum / pairs

**Design**: trade relative strength entre BTC/ETH/SOL — long o que está relativamente forte, short o que está fraco.

**Custo**: alto — requer mudar o framework de backtest (atualmente single-asset). Mudança arquitetural.

**Prior de payoff**: médio-alto se funciona, mas custo não é fase única.

### Candidato E: orderbook/microestrutura

**Design**: volume-weighted features, liquidity imbalance. Requer dados além de OHLCV 1h.

**Custo**: muito alto — precisa orderbook/tape data não ingestada.

## Recomendação

Nenhum dos candidatos A/B/C tem prior claro de payoff acima do custo de implementação + validação (provavelmente ~6-10 runs validation + 2-4h código + ADRs). Candidato D tem prior maior mas custo arquitetural alto.

Opções:

1. **Implementar Candidato C (ATR/Keltner)** — única hipótese estrutural realmente diferenciável sem alterar framework. 2-4h de código + 3-6 runs validation. Payoff incerto mas maior entre opções low-cost.

2. **Pausar pesquisa ativa** — aceitar stack 13 combos como estado estável. Reabrir quando houver (a) novos dados/ativos (bull ≠ bear), (b) hipótese nova emergir de observação de live trading, (c) framework mudar.

3. **Implementar Candidato D (cross-sectional)** — aposta maior, custo maior. Requer ADR de framework mudança.

4. **Implementar A ou B mesmo assim** — para ter Padrão 43 empiricamente testado com engines de família realmente diferente. Valor de informação, não de edge.

## Decisão pendente

Aguardo escolha do usuário.

## Não-alvo

- Não implementar todos candidatos — compromisso de escopo
- Não estender framework para MTF signals sem hipótese concreta (já discutido no contexto ADR-0167/0168)
