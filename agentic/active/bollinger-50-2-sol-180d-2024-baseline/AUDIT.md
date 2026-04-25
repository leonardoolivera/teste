# AUDIT.md — K.4 Bollinger 50/2 SOL 180d 2024

release_decision: canary_only

## release_decision

**`canary_only`** — 10º do protocolo. Série K completa 4/4.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%     | 61.54%    | **OK** |
| Critério 2: max_drawdown ≤ 35%          | 6.96%     | OK     |
| Critério 3: spread+10 / baseline ≥ 0.95 | 0.984     | OK     |

## Blockers

Módulo `canary-trade` inexistente.

## Findings

1. **Edge sobrevive janela 2.5× mais longa.** Hit 61.54% com 39 trades.
2. **Fe neutro (9990.02, −0.10%)** — janela longa perde volume de trades sem compensar
   em magnitude. Caso similar a J.3 ETH.
3. **Série K completa 4/4 `canary_only`.** Sensibilidade de hiperparâmetros: **BAIXA**.

## Lições

1. **Todos os 4 pontos de sensibilidade passam hard gate** (hit ∈ [59.54%, 67.82%]).
   Edge NÃO é ajustado fino ao ponto (20, 2.0).
2. **Configuração 20/2.0 (baseline J.1) está próxima do ótimo global** neste tape —
   K.1 (1.5) tem fe maior mas hit menor; K.3 (window=10) tem mdd menor mas stress no limite;
   K.2 (2.5) e K.4 (50) têm fe neutro.
3. **Dimensões ainda não testadas:** timeframe (15m/30m), segunda família (RSI), combinação
   com filtro de regime.

## Recomendações

- **Série K encerra sensibilidade de hiperparâmetros SOL 2024.** 4/4 passam.
- **Próxima direção candidata:** K.5+ sobre BTC 2024 (cross-asset) OU série L com timeframe
  diferente (15m/30m).
