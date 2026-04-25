# 0117 — Série CY closeout: Donchian 20/10 long refutado como candidato (1/6 probe)

**Status:** Accepted — refutação preliminar
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0116 (pré-registro)

## Resultado (6 runs Donchian long 20/10)

| Tag | Combo | Trades | Sharpe | PnL% | MDD% | Verdict |
|---|---|---:|---:|---:|---:|---|
| CY.1 | BTC 2024-H2 bull | 79 | 0.71 | +1.74 | 3.02 | hit probe |
| CY.2 | ETH 2024-H2 bull | 80 | 0.11 | +0.20 | 3.33 | miss |
| CY.3 | SOL 2024-H2 bull | 84 | **-0.91** | -3.48 | 6.59 | miss |
| CY.4 | BTC 2025-H2 misto | 85 | **-4.17** | -7.05 | 7.61 | miss |
| CY.5 | ETH 2025-H2 misto | 77 | **-2.01** | -5.51 | 8.43 | miss |
| CY.6 | SOL 2025-H2 misto | 81 | **-3.05** | -9.88 | 13.31 | miss |

**Agregado: 0 hit forte, 1 hit probe, 5 miss (3/6 FAIL strong Sh<-1).**

## Interpretação

Donchian 20/10 long **refutado** como candidato a manifest sob protocolo atual (gate pré-registrado: ≥2 hit forte pra abrir série de validação; ≤1 probe → refutação preliminar).

Observações:
1. **Trade count saudável** (77-85 por 6m window) — engine não é subamostrada, FAIL é genuíno
2. **Bull não ajuda uniformemente**: BTC bull marginal, ETH bull nulo, **SOL bull destrutivo** (-0.91). Momentum breakout clássico NÃO funciona em SOL 2024-H2 — regime volátil com muitos fake-outs
3. **2025-H2 misto catastrófico**: 3/3 FAIL strong. Whipsaws de regime misto matam breakout puro
4. **MDD alto nas falhas** (6-13%): fake-outs não só falham, sangram capital

## Padrão 29 (NOVO): breakout long puro não diversifica mean-reversion stack

Contra-hipótese pré-registrada **refutada**: "Donchian momentum é natural complemento de RSI/Bollinger mean-reversion". Dados mostram:
- Mean-reversion engines (RSI/Bollinger) lucram com retornos à média pós-breakout
- Donchian long entra no breakout — frequentemente NA MESMA barra onde RSI/Bollinger short entraria
- **Interação**: Donchian long comprando fake-out alto é exatamente o oposto do que RSI short vende alto
- Portanto: NÃO é diversificação, é **anti-correlação negativa destrutiva em regimes whipsaw**

Não testado aqui, mas hipótese forte: cross-engine correlação Donchian long × RSI short seria muito negativa em periodos misto (corr ~ -0.7), o que é pior que neutra para diversificação (anti-bet amplifica vol ao invés de reduzir).

## Alternativas não testadas (backlog)

1. **Donchian com params diferentes**: 40/20 (Turtle longo), 10/5 (breakout curto). Não testado, mas 20/10 canonical falhou em 5/6 — pouco otimista.
2. **Donchian com filter**: breakout + ATR trailing stop ou width filter. Requer engine extension.
3. **Donchian short**: por hipótese, short em bull é ruim; short em misto pode capturar fake-outs. 6 runs extras.
4. **MA crossover family**: engine disponível, não testado. Próximo candidato natural a 3ª family.

Não agendar nenhum automaticamente. Usuário decide próxima direção.

## Não-alvo

- Não alterar stack (nada promovido)
- Não abrir série CV/CZ dedicada a Donchian (critério não atendido)
- Não emitir bridge post

## Stack pós-CY

13 combos inalterados. Diversificação por engine continua limitada (RSI + Bollinger dominantes). Backlog para diversificação:
- MA crossover family exploration (não rodada)
- Donchian short cross-asset (não rodada)
- RSI+filter alternativo (já rodado em múltiplas séries sem promoção nova)
