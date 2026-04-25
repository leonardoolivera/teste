# VALIDATION.md — J.2 Bollinger 20/2 BTC 180d 2024

## Testes executados

- Suíte preservada em `337 passed, 1 skipped`.
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos.

## Conformidade (ADR-0025)

| Critério                                  | Limite  | Observado              | Status |
| ----------------------------------------- | ------- | ---------------------- | ------ |
| 1. hit_rate baseline                      | ≥ 45%   | **68.24%**             | **OK** |
| 2. max_drawdown baseline                  | ≤ 35%   | 3.62%                  | OK     |
| 3. spread+10 / baseline                   | ≥ 0.95  | 9911.98/10252.14=0.967 | OK     |
| Corroboração: fold mín hit > 45%          | > 45%   | 64.71% (fold 2)        | OK     |

**4/4 folds cruzam 45% com margem.** Fold min=64.71% é o maior fold-min do protocolo.

## Invariantes

- ADR-0019 17ª confirmação: `fee+10 ≡ spread+10 = 9911.98` bit-a-bit.
- ADR-0010 monotonicity ✅.
