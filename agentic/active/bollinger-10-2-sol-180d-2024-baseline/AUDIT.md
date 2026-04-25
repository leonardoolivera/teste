# AUDIT.md — K.3 Bollinger 10/2 SOL 180d 2024

release_decision: canary_only

## release_decision

**`canary_only`** — 9º do protocolo.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%     | 59.54%    | **OK** |
| Critério 2: max_drawdown ≤ 35%          | **2.26%** (menor do protocolo) | OK |
| Critério 3: spread+10 / baseline ≥ 0.95 | 0.951     | OK     |

## Blockers

Módulo `canary-trade` inexistente.

## Findings

1. **Menor mdd do protocolo (2.26%).** Janela curta → posições curtas → menos exposição.
2. **Maior frequência (131 trades)** — mais robusto à variância de folds.
3. **Stress no limite.** `spread+10` ratio 0.951 é o mais próximo de violar 0.95 do protocolo.

## Lições

1. **Eixo `window` mapeia trade-off mdd/custo-sensibilidade:**
   - 10: mdd mínimo, stress no limite.
   - 20: balanceado (baseline).
   - 50: mdd maior, stress folgado.
2. **Edge sobrevive janela 2× mais curta.** Baixa sensibilidade no eixo temporal-interno.
