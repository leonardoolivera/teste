# VALIDATION.md — H.9 Donchian 20/10 ETH 180d + SMA

## Testes executados

- Suíte `305 passed, 1 skipped` preservada.
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos.

## Conformidade

| Critério                                     | Limite  | Observado               | Status    |
| -------------------------------------------- | ------- | ----------------------- | --------- |
| 1. hit_rate baseline                         | ≥ 45%   | **32.29%**              | **VIOLA** |
| 2. max_drawdown baseline                     | ≤ 35%   | 6.64%                   | OK        |
| 3. spread+10 / baseline                      | ≥ 0.95  | 10119.56/10504.18=0.9634| OK        |
| Corroboração: final_equity > 10000           | > 10000 | **10504.18**            | **OK**    |

**Primeiro piloto do protocolo com baseline > 10000!** Apenas critério 1 viola (hit_rate).

## Invariantes

- ADR-0019 11ª confirmação: `fee+10 ≡ spread+10 = 10119.56` bit-a-bit (primeira vez com fe > 10000 + filtro ativo!).
- ADR-0010 monotonicity. ✅
