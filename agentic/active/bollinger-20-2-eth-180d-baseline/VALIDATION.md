# VALIDATION.md — I.3 Bollinger 20/2 ETH 180d

## Testes executados

- Suíte preservada em `337 passed, 1 skipped`.
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos.

## Conformidade (ADR-0025)

| Critério                                  | Limite  | Observado              | Status |
| ----------------------------------------- | ------- | ---------------------- | ------ |
| 1. hit_rate baseline                      | ≥ 45%   | **63.41%**             | **OK** |
| 2. max_drawdown baseline                  | ≤ 35%   | 5.17%                  | OK     |
| 3. spread+10 / baseline                   | ≥ 0.95  | 9729.39/10057.17=0.967 | OK     |
| Rank top-3 (N=15)                         | top-3   | **3/15** (score 7.12)  | OK     |
| Corroboração: fold mín hit > 45%          | > 45%   | 50.00% (folds 2+3)     | OK     |

**Todos os 4 folds cruzam 45%.** Pior fold em 50% exato.

## Invariantes

- ADR-0019 15ª confirmação: `fee+10 ≡ spread+10 = 9729.39` bit-a-bit.
- ADR-0010 monotonicity ✅.
