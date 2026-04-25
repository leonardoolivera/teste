# VALIDATION.md — H.7 Donchian 10/5 BTC 180d

## Testes executados

- Suíte `305 passed, 1 skipped` preservada (piloto não toca `src/` ou `tests/`).
- Pipeline `alpha-forge validate` executou sem erros; 4 JSONs persistidos.

## Conformidade

| Critério                                 | Limite | Observado         | Status    |
| ---------------------------------------- | ------ | ----------------- | --------- |
| 1. hit_rate baseline                     | ≥ 45%  | **31.77%**        | **VIOLA** |
| 2. max_drawdown baseline                 | ≤ 35%  | 5.94%             | OK        |
| 3. spread+10 / baseline                  | ≥ 0.95 | 8766.17/9532.45=0.9196 | **VIOLA** |
| Corroboração: trade_count ≠ 110 (vs H.1) | ≠ 110  | 192               | OK        |

**Dupla violação:** critério 1 + critério 3 (janela menor → mais trades → maior sensibilidade a custos, critério 3 quebra pela segunda vez no protocolo, primeira foi H.2c short).

## Invariantes

- ADR-0019 9ª confirmação: `fee+10 ≡ spread+10 = 8766.17` bit-a-bit.
- ADR-0010 monotonicity: `slip+5 < baseline` e `spread+10 < baseline`. ✅
