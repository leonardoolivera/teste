# VALIDATION.md — H.8 Donchian 40/20 BTC 180d

## Testes executados

- Suíte `305 passed, 1 skipped` preservada.
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos.

## Conformidade

| Critério                          | Limite | Observado              | Status    |
| --------------------------------- | ------ | ---------------------- | --------- |
| 1. hit_rate baseline              | ≥ 45%  | **24.49%**             | **VIOLA** |
| 2. max_drawdown baseline          | ≤ 35%  | 6.51%                  | OK        |
| 3. spread+10 / baseline           | ≥ 0.95 | 9333.41/9528.27=0.9796 | OK        |
| Corroboração trade_count < 110    | estrito| **49 < 110**           | OK (−55%) |

Apenas critério 1 viola — porém os critérios 2, 3 e corroboração todos passam com folga recorde.

## Invariantes

- ADR-0019 10ª confirmação: `fee+10 ≡ spread+10 = 9333.41` bit-a-bit.
- ADR-0010 monotonicity. ✅
