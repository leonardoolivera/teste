# VALIDATION.md — H.10 Donchian 20/10 SOL 180d

## Testes executados

- Suíte `305 passed, 1 skipped` preservada.
- Pipeline `alpha-forge validate` limpo; 4 JSONs persistidos.

## Conformidade

| Critério                                  | Limite | Observado               | Status    |
| ----------------------------------------- | ------ | ----------------------- | --------- |
| 1. hit_rate baseline                      | ≥ 45%  | **31.07%**              | **VIOLA** |
| 2. max_drawdown baseline                  | ≤ 35%  | 14.55%                  | OK        |
| 3. spread+10 / baseline                   | ≥ 0.95 | 8709.91/9119.73=0.9551  | OK        |
| Corroboração: fold máx hit > 45%          | > 45%  | **47.62% (fold 0)**     | **OK**    |

**Corroboração passa:** fold 0 hit=47.62% — terceiro fold do protocolo a cruzar 45% (após H.3 fold 2 e H.5 fold 1). Apenas critério 1 (hit agregado) viola.

## Invariantes

- ADR-0019 12ª confirmação: `fee+10 ≡ spread+10 = 8709.91` bit-a-bit.
- ADR-0010 monotonicity. ✅
