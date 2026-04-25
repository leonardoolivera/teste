# VALIDATION.md — K.3 Bollinger 10/2 SOL 180d 2024

## Testes executados

- Suíte preservada em `337 passed, 1 skipped`.
- Pipeline `alpha-forge validate` limpo.

## Conformidade (ADR-0025)

| Critério                                  | Limite  | Observado                | Status |
| ----------------------------------------- | ------- | ------------------------ | ------ |
| 1. hit_rate baseline                      | ≥ 45%   | **59.54%**               | **OK** |
| 2. max_drawdown baseline                  | ≤ 35%   | **2.26%** (menor do protocolo) | OK |
| 3. spread+10 / baseline                   | ≥ 0.95  | 10146.94/10671.75=0.951  | OK     |
| Corroboração: fold mín hit > 45%          | > 45%   | 56.00% (fold 2)          | OK     |

**4/4 folds cruzam 45%.**

## Invariantes

- ADR-0019 21ª confirmação: `fee+10 ≡ spread+10 = 10146.94`.
- ADR-0010 monotonicity ✅.
