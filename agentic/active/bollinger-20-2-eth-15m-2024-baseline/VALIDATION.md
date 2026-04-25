# VALIDATION.md — L.3 Bollinger 20/2 ETH 15m 2024

## Testes executados

- Suíte preservada em `337 passed, 1 skipped`.
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos.

## Conformidade (ADR-0025)

| Critério                                  | Limite  | Observado              | Status |
| ----------------------------------------- | ------- | ---------------------- | ------ |
| 1. hit_rate baseline                      | ≥ 45%   | 61.76%                 | OK     |
| 2. max_drawdown baseline                  | ≤ 35%   | 9.32%                  | OK     |
| 3. spread+10 / baseline                   | ≥ 0.95  | 8357.51/9769.61=0.855  | **VIOLADO** |
| Corroboração: fold mín hit > 45%          | > 45%   | 52.24%                 | OK     |

**Critério 3 violado por margem ainda maior que L.1/L.2 (0.855).** Fe baseline
também < capital (9769.61 < 10000). Trio L completo: 3/3 `fail`.

## Invariantes

- ADR-0019 25ª confirmação: `fee+10 ≡ spread+10 = 8357.51` bit-a-bit.
- ADR-0010 monotonicity ✅.
