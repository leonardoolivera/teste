# AUDIT.md — J.3 Bollinger 20/2 ETH 180d 2024

release_decision: canary_only

## release_decision

**`canary_only`** — sexto do protocolo. Terceiro da Série J. **Série J completa 3/3
`canary_only`.**

| Gate                                    | Observado              | Status |
| --------------------------------------- | ---------------------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%     | **71.76%** (máximo do protocolo) | **OK** |
| Critério 2: max_drawdown ≤ 35%          | 5.93%                  | OK     |
| Critério 3: spread+10 / baseline ≥ 0.95 | 0.966                  | OK     |

## Blockers

Módulo `canary-trade` inexistente.

## Findings

1. **Hit máximo do protocolo (71.76%).** Supera I.3 (63.41%), J.1 (67.82%) e J.2 (68.24%).
   ETH 2024-H2 é a janela mais favorável a mean-reversion de todos os 6 pilotos Bollinger.
2. **Paradoxo hit-vs-fe.** Hit 71.76% mas fe=9977.19 (−0.23%). Vencedores são ligeiramente
   menores que perdedores em magnitude — configuração 10k/0.1/2.0x pode estar
   sub-otimizada para esta distribuição específica. Hard gate passa; preservação de capital
   é essencialmente neutra.
3. **Folds 1 e 3 com hit > 80%** (83.33% e 81.25%) — dispersão fold-a-fold intermediária
   (62.50–83.33%, std 9.75 pp).
4. **ADR-0019 18ª confirmação** (`fee+10 ≡ spread+10 = 9637.58`).

## Lições

1. **Série J fecha com 3/3 canary_only + Série I 3/3 = 6/6 Bollinger passam.** Robustez
   temporal CONFIRMADA em 3 assets × 2 janelas independentes.
2. **"Hit alto" e "fe alto" são métricas diferentes, não correlacionadas 1:1.** J.3
   é prova concreta: hit 71.76% pode coexistir com fe marginalmente negativo quando
   distribuição de magnitude é desfavorável. Isso explica porque ADR-0024 pesa ambos.
3. **2024-H2 é janela mais favorável a mean-reversion que 2025-H2 em 3/3 assets.**
   SOL +1.97 pp hit; BTC +2.39 pp; ETH +8.35 pp. Hipótese: 2024-H2 teve mais regime
   lateral; 2025-H2 teve mais trend (SOL/BTC subiram fortemente).
4. **Próximo handoff provável: J.2 BTC 2024.** Combina hit alto (68.24%), fe positivo
   (+2.52%), menor mdd (3.62%), maior fold-homogeneidade (std 3.48 pp), cross-window
   validado. Pré-requisitos: OOS Sharpe + aprovação.

## Recomendações

- **Re-ranquear N=18** para ver nova ordem com 6 Bollinger.
- **Abrir Série K** com dimensões ainda não testadas: (a) hiperparâmetros (num_std 1.5/2.5),
  (b) timeframe menor (15m/30m), (c) segunda família mean-reversion (RSI).
- **Handoff BotBinance destravado para J.2 BTC 2024** (sujeito a OOS Sharpe + aprovação).
