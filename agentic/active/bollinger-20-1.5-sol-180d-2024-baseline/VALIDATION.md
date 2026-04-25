# VALIDATION.md — K.1 Bollinger 20/1.5 SOL 180d 2024

## Testes executados

- Suíte preservada em `337 passed, 1 skipped`.
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos.

## Conformidade (ADR-0025)

| Critério                                  | Limite  | Observado                | Status |
| ----------------------------------------- | ------- | ------------------------ | ------ |
| 1. hit_rate baseline                      | ≥ 45%   | **64.96%**               | **OK** |
| 2. max_drawdown baseline                  | ≤ 35%   | 4.01%                    | OK     |
| 3. spread+10 / baseline                   | ≥ 0.95  | 10403.48/10872.74=0.957  | OK     |
| Corroboração: fold mín hit > 45%          | > 45%   | 46.15% (fold 4)          | OK     |

**4/4 folds cruzam 45%.**

## Invariantes

- ADR-0019 19ª confirmação: `fee+10 ≡ spread+10 = 10403.48`.
- ADR-0010 monotonicity ✅.
