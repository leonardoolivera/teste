# AUDIT.md — K.1 Bollinger 20/1.5 SOL 180d 2024

release_decision: canary_only

## release_decision

**`canary_only`** — 7º do protocolo. Primeiro da Série K.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%     | **64.96%** | **OK** |
| Critério 2: max_drawdown ≤ 35%          | 4.01%     | OK     |
| Critério 3: spread+10 / baseline ≥ 0.95 | 0.957     | OK     |

## Blockers

Módulo `canary-trade` inexistente.

## Findings

1. **Edge robusto a redução de threshold.** `num_std=1.5` gera +34% trades e mantém
   hit >60%. Não é ajuste fino ao ponto 2.0.
2. **Maior fe do protocolo (10872.74).** Volume compensa ligeiro sacrifício em precisão.
3. **Fold 4 em 46.15%** (marginal mas >45%).

## Lições

1. **Banda mais estreita é viável.** Não colapsa o edge; amplia retorno esperado.
2. **Série K abre confirmando sensibilidade baixa na dimensão `num_std`.** K.2 (2.5) fecha o eixo.
