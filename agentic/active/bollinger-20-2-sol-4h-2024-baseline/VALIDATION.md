# VALIDATION.md — M.1 Bollinger 20/2 SOL 4h 2024

## Testes executados

- Suíte preservada em `337 passed, 1 skipped`.
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos.

## Conformidade (ADR-0025)

| Critério                                  | Limite  | Observado              | Status |
| ----------------------------------------- | ------- | ---------------------- | ------ |
| 1. hit_rate baseline                      | ≥ 45%   | 57.14% (21 trades)     | OK     |
| 2. max_drawdown baseline                  | ≤ 35%   | 6.99%                  | OK     |
| 3. spread+10 / baseline                   | ≥ 0.95  | 9683.54/9766.99=0.9915 | **OK** (primeiro cross-timeframe com folga) |
| Corroboração: fold mín hit > 45%          | > 45%   | 0.00% (fold 3, 1 trade)| VIOLADO |

**Critério 3 passa folgado** (0.9915, margem 40 bps sobre limite 0.95) — confirma hipótese de que 4h
elimina o problema de custos que quebrou Série L. **Porém fe baseline < capital** (9766.99 < 10000):
edge econômico ausente mesmo sem stress. Corroboração WF violada (fold 3 com 1 trade, hit=0%).

## Invariantes

- ADR-0019 26ª confirmação: `fee+10 ≡ spread+10 = 9683.54` bit-a-bit.
- ADR-0010 monotonicity ✅.
