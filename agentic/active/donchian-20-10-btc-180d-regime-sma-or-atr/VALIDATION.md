# VALIDATION.md — H.6 Donchian + Composite(sma OR atr)

## Testes executados

- Suíte pós-H.5b dívida: **305 passed, 1 skipped** (novo test signal-emission).
- Pipeline `alpha-forge validate` executou sem erros; 4 JSONs em `results/validation/donchian-20-10-btc-180d-regime-sma-or-atr/`.

## Conformidade

| Critério                                  | Limite       | Observado            | Status     |
| ----------------------------------------- | ------------ | -------------------- | ---------- |
| 1. hit_rate baseline                      | ≥ 45%        | **26.79%**           | **VIOLA**  |
| 2. max_drawdown baseline                  | ≤ 35%        | 10.26%               | OK         |
| 3. spread+10 / baseline                   | ≥ 0.95       | 8683.06/9128.87=0.9511 | OK       |
| Corroboração: trade_count > 114 (OR perm.)| estrito      | 112 < 114            | **VIOLA**  |

**Dupla falha:** critério 1 (hit_rate) + corroboração (OR NÃO superou cada filtro individual em trade_count sobre o período inteiro — reflete o mesmo fenômeno de fragmentação documentado em H.5, agora na direção oposta: OR em trade_count pode ser menor que cada individual porque trades curtos agregam em trades longos contínuos).

## Invariantes

- ADR-0019 `fee+10 ≡ spread+10 = 8683.06` bit-a-bit — **8ª confirmação**.
- ADR-0010 monotonicity: `slip+5.fe < baseline.fe` e `spread+10.fe < baseline.fe`. ✅
- ADR-0023 canonical: `or(atr_regime:...,sma_slope:...)` com filtros reordenados lex. ✅
- ADR-0023 property 2 **a nível de signal-emission** (não trade_count) — preserved: test property-based passa sobre dataset sintético.
