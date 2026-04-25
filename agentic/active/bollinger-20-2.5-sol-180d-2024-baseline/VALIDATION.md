# VALIDATION.md — K.2 Bollinger 20/2.5 SOL 180d 2024

## Testes executados

- Suíte preservada em `337 passed, 1 skipped`.
- Pipeline `alpha-forge validate` limpo.

## Conformidade (ADR-0025)

| Critério                                  | Limite  | Observado             | Status |
| ----------------------------------------- | ------- | --------------------- | ------ |
| 1. hit_rate baseline                      | ≥ 45%   | **62.00%**            | **OK** |
| 2. max_drawdown baseline                  | ≤ 35%   | 3.42%                 | OK     |
| 3. spread+10 / baseline                   | ≥ 0.95  | 9990.99/10191.16=0.980 | OK    |
| Corroboração: fold mín hit > 45%          | > 45%   | 44.44% (fold 2)       | **marginal** |

**3/4 folds cruzam 45%;** fold 2 em 44.44% (abaixo por margem mínima). Baseline passa hard gate.

## Invariantes

- ADR-0019 20ª confirmação: `fee+10 ≡ spread+10 = 9990.99`.
- ADR-0010 monotonicity ✅.
