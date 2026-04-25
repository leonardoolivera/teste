# VALIDATION.md — M.2 Bollinger 20/2 BTC 4h 2024

## Testes executados

- Suíte preservada em `337 passed, 1 skipped`.
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos.

## Conformidade (ADR-0025)

| Critério                                  | Limite  | Observado              | Status |
| ----------------------------------------- | ------- | ---------------------- | ------ |
| 1. hit_rate baseline                      | ≥ 45%   | 52.63% (19 trades)     | OK     |
| 2. max_drawdown baseline                  | ≤ 35%   | 4.38%                  | OK     |
| 3. spread+10 / baseline                   | ≥ 0.95  | 9856.70/9932.49=0.9924 | **OK** |
| Corroboração: fold mín hit > 45%          | > 45%   | 0.00% (fold 3, 2 trades)| VIOLADO |

**Critérios 1-3 passam** mas fe baseline = 9932.49 < 10000 (−0.68%). Replica padrão de M.1:
4h elimina custo mas amostra pequena impede edge.

## Invariantes

- ADR-0019 27ª confirmação: `fee+10 ≡ spread+10 = 9856.70` bit-a-bit.
- ADR-0010 monotonicity ✅.
