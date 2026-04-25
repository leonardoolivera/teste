# AUDIT.md — P.2 Bollinger BTC 1h 2024 + atr_regime

release_decision: canary_only

## release_decision

**`canary_only`** — 35º piloto. **DOMINA J.2 em todas as dimensões
operacionais** (hit +5.37 pp, fe +64.79, ratio +0.0053, MC p5 +49.60, trades
−15%). Primeiro piloto do protocolo a superar J.2. **Candidato primário a
novo handoff BotBinance.**

| Gate                                    | Observado | Status |
| --------------------------------------- | --------: | ------ |
| Critério 1: hit_rate baseline ≥ 45%     |    73.61% |     OK |
| Critério 2: max_drawdown ≤ 35%          |     3.62% |     OK |
| Critério 3: spread+10 / baseline ≥ 0.95 |    0.9721 |     OK |

## Blockers

`canary-trade` inexistente (impossibilidade operacional continua — mesmo
com P.2 superior, handoff real fica bloqueado até módulo ser construído).

## Findings

1. **Filtro ATR captura valor real em mean-reversion BTC 1h 2024-H2.**
   Trade count cai de 85 → 72 (−15%) mas hit sobe de 68.24% → 73.61%
   (+5.37 pp). Sinais filtrados eram, em média, **piores que os
   preservados**. Hipótese SPEC confirmada: regimes de baixa volatilidade
   têm bandas Bollinger estreitas sem edge real.
2. **`fee+10` final_equity > 10000** — primeira vez no protocolo que cenário
   de stress termina acima do capital inicial. **Edge sobrevive stress.**
3. **Fold 2 hit=84.62%** — highest single-fold hit do protocolo inteiro.
4. **MC p5 = 9971.33** é o **2º melhor dos 15 `canary_only`** (atrás apenas
   de P.3=9995.84). Risco de cauda inferior dos menores.
5. **ADR-0019 35ª confirmação** (`fee+10 ≡ spread+10 = 10028.5915`).
6. **WF folds todos ≥ 72%** — nunca visto antes no protocolo.

## Lições

1. **Filtro de volatilidade é mais eficaz que filtro direcional em BTC
   mean-reversion 2024-H2.** P.1 (sma_slope) apenas reordena timing;
   P.2 (atr_regime) remove sinais ruins. Família de filtro importa
   qualitativamente, não só quantitativamente — confirma Série H (H.3
   SMA vs H.4 ATR vs H.5 AND em Donchian long) agora replicada em
   Bollinger mean-reversion.
2. **"Diversificar família" < "adicionar filtro ao sweet spot"** como
   estratégia de ganho: 3 pilotos RSI (Série N) custaram muito mais código
   e geraram ganhos 0 vs handoff; 1 filtro ATR (P.2) **ganha em todas as
   dimensões** sem novo código.
3. **Série P deveria ter sido executada antes da Série N** em termos de
   valor esperado operacional. Lição para sequenciamento futuro: primeiro
   aperfeiçoar o melhor piloto, depois explorar novas famílias.

## Recomendações

- **P.2 é o novo candidato primário a handoff BotBinance** (superando J.2
  em todas as métricas). Verificar no leaderboard N=36 se o score
  composto confirma (esperado: score > 7.64).
- **Continuar P.3** (composite AND) para testar se adicionar sma_slope a
  atr_regime traz ganho adicional ou é redundante.
- **Próxima Série Q candidata:** replicar P.2 cross-asset (J.1 SOL +
  atr_regime; J.3 ETH + atr_regime) para validar que edge do filtro ATR
  não é BTC-específico.
