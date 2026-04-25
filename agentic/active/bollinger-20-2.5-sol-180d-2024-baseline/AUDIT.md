# AUDIT.md — K.2 Bollinger 20/2.5 SOL 180d 2024

release_decision: canary_only

## release_decision

**`canary_only`** — 8º do protocolo. Segundo da Série K.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%     | **62.00%** | **OK** |
| Critério 2: max_drawdown ≤ 35%          | 3.42%     | OK     |
| Critério 3: spread+10 / baseline ≥ 0.95 | 0.980     | OK     |

## Blockers

Módulo `canary-trade` inexistente.

## Findings

1. **Edge sobrevive banda larga (2.5σ).** Hit 62% com 50 trades (seletivo).
2. **Melhor robustez a stress do protocolo** (spread+10 ratio 0.980 vs média 0.966).
   Banda larga = menos trades = menos sensível a custos.
3. **Fold 2 em 44.44%** — marginal abaixo de 45%; hard gate baseline passa.

## Lições

1. **Eixo `num_std` mapeia trade-off volume/seletividade previsível:**
   - 1.5: 117 trades, hit 64.96%, fe máximo.
   - 2.0: 87 trades, hit 67.82%, balanceado.
   - 2.5: 50 trades, hit 62.00%, robusto a custos.
2. **Todos os 3 pontos de `num_std` passam hard gate.** Sensibilidade baixa neste eixo.
