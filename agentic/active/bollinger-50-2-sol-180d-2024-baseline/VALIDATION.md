# VALIDATION.md — K.4 Bollinger 50/2 SOL 180d 2024

## Testes executados

- Suíte preservada em `337 passed, 1 skipped`.
- Pipeline `alpha-forge validate` limpo.

## Conformidade (ADR-0025)

| Critério                                  | Limite  | Observado              | Status |
| ----------------------------------------- | ------- | ---------------------- | ------ |
| 1. hit_rate baseline                      | ≥ 45%   | **61.54%**             | **OK** |
| 2. max_drawdown baseline                  | ≤ 35%   | 6.96%                  | OK     |
| 3. spread+10 / baseline                   | ≥ 0.95  | 9834.20/9990.02=0.984  | OK     |
| Corroboração: fold mín hit > 45%          | > 45%   | 50.00% (fold 4)        | OK     |

**4/4 folds cruzam 45%.**

## Invariantes

- ADR-0019 22ª confirmação: `fee+10 ≡ spread+10 = 9834.20`.
- ADR-0010 monotonicity ✅.

## Anomalia observada

`final_equity` baseline = 9990.02 (−0.10%, neutro). Apesar de hit 61.54% e fold_min 50%,
fe baseline é marginal — similar ao padrão observado em J.3 ETH (hit alto, fe neutro).
Janela longa captura menos oportunidades; trades maiores não compensam volume menor
perfeitamente. Hard gate passa.
