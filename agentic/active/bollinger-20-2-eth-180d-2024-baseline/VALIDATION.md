# VALIDATION.md — J.3 Bollinger 20/2 ETH 180d 2024

## Testes executados

- Suíte preservada em `337 passed, 1 skipped`.
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos.

## Conformidade (ADR-0025)

| Critério                                  | Limite  | Observado               | Status |
| ----------------------------------------- | ------- | ----------------------- | ------ |
| 1. hit_rate baseline                      | ≥ 45%   | **71.76%** (maior do protocolo) | **OK** |
| 2. max_drawdown baseline                  | ≤ 35%   | 5.93%                   | OK     |
| 3. spread+10 / baseline                   | ≥ 0.95  | 9637.58/9977.19=0.966   | OK     |
| Corroboração: fold mín hit > 45%          | > 45%   | 62.50% (fold 4)         | OK     |

**4/4 folds cruzam 45% com margem ampla.**

## Invariantes

- ADR-0019 18ª confirmação: `fee+10 ≡ spread+10 = 9637.58` bit-a-bit.
- ADR-0010 monotonicity ✅.

## Anomalia observada

`final_equity` baseline = 9977.19 (marginalmente < 10000) apesar de hit=71.76%. Caso
raro: alta proporção de trades vencedores mas magnitude média negativa (vencedores
pequenos, perdedores ocasionais maiores). Hard gate (hit) passa; critério 2 e 3
passam; ranking vai pesar fe baixo no `composite_score`.
