# VALIDATION.md — J.1 Bollinger 20/2 SOL 180d 2024

## Testes executados

- Suíte preservada em `337 passed, 1 skipped`.
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos em `results/validation/bollinger-20-2-sol-180d-2024-baseline/`.

## Conformidade (ADR-0025)

| Critério                                  | Limite  | Observado              | Status |
| ----------------------------------------- | ------- | ---------------------- | ------ |
| 1. hit_rate baseline                      | ≥ 45%   | **67.82%**             | **OK** |
| 2. max_drawdown baseline                  | ≤ 35%   | **3.43%**              | OK     |
| 3. spread+10 / baseline                   | ≥ 0.95  | 10335.23/10684.24=0.967 | OK    |
| Corroboração: fold mín hit > 45%          | > 45%   | 47.06% (fold 2)        | OK     |

**Todos os 4 folds cruzam 45%.** Pior fold em 47.06% (marginalmente acima).

## Invariantes

- ADR-0019 16ª confirmação: `fee+10 ≡ spread+10 = 10335.23` bit-a-bit.
- ADR-0010 monotonicity ✅.
- ADR-0026 causalidade (via property tests I.1) ✅.
