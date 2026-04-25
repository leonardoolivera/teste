# VALIDATION.md — I.2 Bollinger 20/2 BTC 180d

## Testes executados

- Suíte preservada em `337 passed, 1 skipped` (zero mudança em `src/` ou `tests/`).
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos.

## Conformidade (ADR-0025)

| Critério                                  | Limite  | Observado              | Status |
| ----------------------------------------- | ------- | ---------------------- | ------ |
| 1. hit_rate baseline                      | ≥ 45%   | **65.85%**             | **OK** |
| 2. max_drawdown baseline                  | ≤ 35%   | 2.80%                  | OK     |
| 3. spread+10 / baseline                   | ≥ 0.95  | 9703.27/10033.00=0.967 | OK     |
| Rank top-3 (N=15)                         | top-3   | **1/15** (score 7.70)  | OK     |
| Corroboração: fold máx hit > 45%          | > 45%   | 69.23% (fold 4)        | OK     |
| Corroboração: fold mín hit > 45%          | > 45%   | **44.44% (fold 2)**    | **VIOLA (marginal)** |

**Baseline passa critério 1 com folga** (20.85 pp acima do piso). Fold 2 marginalmente
abaixo de 45% (44.44%, −0.56 pp) — único fold do piloto que não cruza. Agregação passa.

## Invariantes

- ADR-0019 14ª confirmação: `fee+10 ≡ spread+10 = 9703.27` bit-a-bit.
- ADR-0010 monotonicity ✅.
- ADR-0003 MC seed=42: p5=9434.37, p50=9860.02, p95=10240.18.
- ADR-0026 causalidade/monotonicidade propriedades já testadas estruturalmente em I.1.
