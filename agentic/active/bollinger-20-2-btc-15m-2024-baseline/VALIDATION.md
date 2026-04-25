# VALIDATION.md — L.2 Bollinger 20/2 BTC 15m 2024

## Testes executados

- Suíte preservada em `337 passed, 1 skipped`.
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos.

## Conformidade (ADR-0025)

| Critério                                  | Limite  | Observado              | Status |
| ----------------------------------------- | ------- | ---------------------- | ------ |
| 1. hit_rate baseline                      | ≥ 45%   | 60.00%                 | OK     |
| 2. max_drawdown baseline                  | ≤ 35%   | 5.11%                  | OK     |
| 3. spread+10 / baseline                   | ≥ 0.95  | 8376.61/9696.67=0.864  | **VIOLADO** |
| Corroboração: fold mín hit > 45%          | > 45%   | 58.62%                 | OK     |

**Critério 3 violado (0.864 < 0.95).** Replica o achado de L.1 em BTC — fragilidade
de 15m é propriedade do timeframe, não idiossincrasia de SOL.

## Invariantes

- ADR-0019 24ª confirmação: `fee+10 ≡ spread+10 = 8376.61` bit-a-bit.
- ADR-0010 monotonicity ✅.
