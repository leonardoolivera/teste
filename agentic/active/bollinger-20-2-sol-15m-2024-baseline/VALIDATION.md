# VALIDATION.md — L.1 Bollinger 20/2 SOL 15m 2024

## Testes executados

- Suíte preservada em `337 passed, 1 skipped` após adição 15m/30m em `TIMEFRAME_DELTAS`.
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos.

## Conformidade (ADR-0025)

| Critério                                  | Limite  | Observado              | Status |
| ----------------------------------------- | ------- | ---------------------- | ------ |
| 1. hit_rate baseline                      | ≥ 45%   | 63.10%                 | OK     |
| 2. max_drawdown baseline                  | ≤ 35%   | 5.53%                  | OK     |
| 3. spread+10 / baseline                   | ≥ 0.95  | 9088.47/10433.99=0.871 | **VIOLADO** |
| Corroboração: fold mín hit > 45%          | > 45%   | 56.45%                 | OK     |

**Critério 3 violado por margem larga (0.871 vs limite 0.95).** Apesar de hit 63.10%,
edge é economicamente frágil em 15m — stress de custos engole >10% do retorno baseline.

## Invariantes

- ADR-0019 23ª confirmação: `fee+10 ≡ spread+10 = 9088.47` bit-a-bit.
- ADR-0010 monotonicity ✅.
