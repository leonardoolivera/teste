# AUDIT.md — M.2 Bollinger 20/2 BTC 4h 2024

release_decision: fail

## release_decision

**`fail`** — replica padrão de M.1. Critérios ADR-0025 passam, mas hipótese SPEC
(fe > capital) violada marginalmente.

| Gate                                    | Observado | Status |
| --------------------------------------- | --------- | ------ |
| Critério 1: hit_rate baseline ≥ 45%     | 52.63%    | OK     |
| Critério 2: max_drawdown ≤ 35%          | 4.38%     | OK     |
| Critério 3: spread+10 / baseline ≥ 0.95 | **0.9924**| **OK** |
| Hipótese SPEC: fe > capital             | 9932.49   | **VIOLADO** (marginal) |
| Corroboração WF fold min hit            | 0.00%     | VIOLADO |

## Blockers

- Fe baseline ligeiramente abaixo de capital (9932.49). Diferença é dentro da margem
  de custos, mas não positiva.
- Apenas 19 trades. Fold 3 com 2 trades e hit 0%.

## Findings

1. **Padrão M.1 replica em BTC.** Critério 3 passa folgado, amostra pequena impede edge.
2. **BTC 4h tem menor mdd do trio M** (4.38% vs 6.99% SOL). Mean-reversion em BTC é mais
   contida em escala 4h por menor volatilidade intra-regime.
3. **Hit menor em BTC (52.63%)** que SOL (57.14%) — BTC 4h teve menos oportunidades claras
   de mean-reversion neste recorte.
4. **ADR-0019 27ª confirmação** (`fee+10 ≡ spread+10 = 9856.70`).

## Lições

1. **Confirmação cross-asset de M.1.** 4h não é caminho para preservar edge; é caminho
   para eliminar custos mas diluir sinal.
2. **Sweet spot 1h é propriedade cross-asset.** J.2 BTC 1h 2024 (rank 1 global, fe=10252.14)
   vs M.2 BTC 4h (fe=9932.49). Diferença ≈ 320 USDT para mesmo asset/janela.

## Recomendações

- M.3 ETH 4h para fechar trio e documentar simetria completa.
- Próxima pesquisa: **RSI 1h cross-asset** (segunda família mean-reversion) ou
  **regime filter + Bollinger 1h** (melhorar edge no sweet spot).
