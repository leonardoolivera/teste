# VALIDATION.md — M.3 Bollinger 20/2 ETH 4h 2024

## Testes executados

- Suíte preservada em `337 passed, 1 skipped`.
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos.

## Conformidade (ADR-0025)

| Critério                                  | Limite  | Observado              | Status |
| ----------------------------------------- | ------- | ---------------------- | ------ |
| 1. hit_rate baseline                      | ≥ 45%   | 43.75% (16 trades)     | **VIOLADO** |
| 2. max_drawdown baseline                  | ≤ 35%   | 8.54%                  | OK     |
| 3. spread+10 / baseline                   | ≥ 0.95  | 9264.56/9327.15=0.9933 | OK     |
| Corroboração: fold mín hit > 45%          | > 45%   | 50.00%                 | OK     |

**Piloto único da Série M a violar critério 1 (hit=43.75% < 45%).** Confirma que em 4h
amostra é insuficiente para sustentar edge; ETH teve variância inferior ao corte mesmo
com 4/4 folds individualmente cruzando 45% em walk-forward.

## Invariantes

- ADR-0019 28ª confirmação: `fee+10 ≡ spread+10 = 9264.56` bit-a-bit.
- ADR-0010 monotonicity ✅.
